"""CLI entrypoint using argparse."""
import argparse
import sys
import json
import time
import os
import tempfile
from app.core.config import Config
from app.core.router import resolve_provider, build_providers
from app.core.prompt_compiler import PromptCompiler
from app.styles.loader import StyleLoader
from app.quality.heuristic import score as heuristic_score
from app.quality.watermark import is_watermarked
from app.quality.style_gate import check_style_gate
from app.quality.vision_judge import judge_with_gemini
from app.core.errors import HanddrawnError, ErrorCode


def _log(msg: str):
    print(msg, file=sys.stderr)


def _print_candidate(idx, status, reason, score=None):
    if status == "PASS":
        mark = "PASS"
    elif status == "REJECT":
        mark = "REJECT"
    else:
        mark = "REVIEW"
    line = f"Candidate #{idx} {mark}"
    if reason:
        line += f" {reason}"
    if score is not None:
        line += f" score={score:.1f}"
    _log(line)


def _generate_with_retry(provider, prompt, negative, width, height, max_attempts=2):
    """Attempt generation with retry for transient errors."""
    last_error = None
    for attempt in range(max_attempts):
        try:
            return provider.generate(
                prompt,
                negative_prompt=negative,
                width=width,
                height=height,
            )
        except HanddrawnError as e:
            last_error = e
            if e.code in (ErrorCode.NETWORK_ERROR, ErrorCode.TIMEOUT, ErrorCode.RATE_LIMIT, ErrorCode.PROVIDER_ERROR):
                time.sleep(1.0 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last_error = e
            time.sleep(1.0 * (attempt + 1))
            continue
    raise last_error or HanddrawnError(ErrorCode.PROVIDER_ERROR, "Generation failed after retries.")


def _safe_filename(prompt: str, style: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in prompt).strip().replace(" ", "_")[:40]
    return f"{style}_{safe}.png"


def _resolve_output_path(args, style: str) -> str:
    base = args.output_dir or getattr(args, "output", None) or "."
    if args.output:
        return args.output
    fname = _safe_filename(args.prompt, style)
    return os.path.join(base, fname)


def _vision_style_pass(style: str, prompt: str, img_data: bytes, vision_key: str) -> tuple[bool, str]:
    """Vision-based style gate with graceful fallback."""
    try:
        vr = judge_with_gemini(img_data, vision_key, timeout=60)
    except Exception:
        sc = check_style_gate(style, prompt)
        return sc["pass"], f"vision_error_fallback({','.join(sc.get('violations', [])[:2])})"
    score = None
    for key in ("final", "handdrawn"):
        val = vr.get(key)
        if isinstance(val, (int, float)):
            score = float(val)
            break
    if score is None:
        sc = check_style_gate(style, prompt)
        return sc["pass"], f"vision_unparsable_fallback({','.join(sc.get('violations', [])[:2])})"
    return score >= 6, f"vision_score={score:.1f}"


def cmd_generate(args):
    config = Config(args.config)
    compiler = PromptCompiler(StyleLoader())
    style = args.style or config.get("default_style", "clean_sketch")
    positive, negative = compiler.compile(args.prompt, style=style)
    providers = resolve_provider(args.provider, config)

    width = args.width or config.get("width", 1024)
    height = args.height or config.get("height", 768)
    if args.candidates is not None and args.candidates < 1:
        candidates_needed = 1
    else:
        candidates_needed = args.candidates or config.get("candidates", 2)
    max_rounds = 2

    vision_key = config.get("providers.gemini.api_key")
    out_path = _resolve_output_path(args, style)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    results = []
    rejections = []
    round_num = 0
    while len(results) < candidates_needed and round_num < max_rounds:
        round_num += 1
        for provider in providers:
            try:
                imgs = _generate_with_retry(provider, positive, negative, width, height)
            except HanddrawnError as e:
                _log(f"WARN {provider.name} failed: {e.message}")
                if e.suggestion:
                    _log(f"  Suggestion: {e.suggestion}")
                continue
            except Exception as e:
                _log(f"WARN {provider.name} unexpected error: {e}")
                continue

            for img in imgs:
                idx = len(results) + len(rejections) + 1

                if len(img.data) < 1000:
                    rejections.append({"candidate": idx, "reason": "INVALID_IMAGE"})
                    _print_candidate(idx, "REJECT", "INVALID_IMAGE")
                    continue

                wm, wm_detail = is_watermarked(img.data, vision_api_key=vision_key)
                if wm:
                    reason = "PROVIDER_WATERMARK"
                    rejections.append({"candidate": idx, "reason": reason, "detail": wm_detail})
                    _print_candidate(idx, "REJECT", reason)
                    continue

                style_pass, style_reason = _vision_style_pass(style, positive, img.data, vision_key)
                if not style_pass:
                    rejections.append({"candidate": idx, "reason": "STYLE_MISMATCH", "detail": style_reason})
                    _print_candidate(idx, "REJECT", f"STYLE_MISMATCH ({style_reason})")
                    continue

                try:
                    q = heuristic_score(img.data)
                except Exception:
                    q = {"final_score": 0.0}
                if q["final_score"] < 0.35:
                    reason = "RENDERING_MISMATCH"
                    rejections.append({"candidate": idx, "reason": reason})
                    _print_candidate(idx, "REJECT", reason)
                    continue

                results.append((img, q))
                _print_candidate(idx, "PASS", "OK", q.get("final_score", 0) * 10)
                if len(results) >= candidates_needed:
                    break
            if len(results) >= candidates_needed:
                break

    if not results:
        _log("ERROR All candidates rejected. Run `python -m app.cli doctor` to check config.")
        sys.exit(1)

    if len(results) == 1:
        best_img, best_q = results[0]
        best_score = best_q.get("final_score", 0) * 10
    else:
        scored = sorted(
            [(q.get("final_score", 0) * 10, img, q) for img, q in results],
            key=lambda x: x[0],
            reverse=True,
        )
        best_score, best_img, best_meta = scored[0]

    refined = False
    if best_score < 7.8:
        edit_provider = None
        for p in providers:
            if getattr(p, "supports_editing", False):
                edit_provider = p
                break
        if edit_provider:
            try:
                refined_prompt = (
                    positive
                    + ", confident graphite/fine-ink contours, natural line-weight variation, "
                    "reduce painterly color, reduce digital gloss, simplify background, "
                    "keep subject recognizable, do not add text or logos"
                )
                refined_imgs = _generate_with_retry(
                    edit_provider, refined_prompt, negative, width, height
                )
                if refined_imgs:
                    wm2, _ = is_watermarked(refined_imgs[0].data, vision_api_key=vision_key)
                    if not wm2:
                        best_img = refined_imgs[0]
                        refined = True
                    else:
                        _log("WARN Refinement produced watermark, keeping original")
            except Exception as e:
                _log(f"WARN Refinement failed: {e}")

    with open(out_path, "wb") as f:
        f.write(best_img.data)

    meta = {
        "provider": best_img.provider,
        "model": best_img.model,
        "style": style,
        "style_score": best_score,
        "handdrawn_score": best_score,
        "watermark": False,
        "refined": refined,
        "rejected_candidates": rejections,
    }
    meta_path = out_path.rsplit(".", 1)[0] + ".json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)

    # stdout 只输出结果路径，Agent/管道可解析
    print(out_path)
    print(meta_path, file=sys.stderr)


def cmd_providers(args):
    print("Available providers:")
    profiles = {
        "auto": "Gemini -> OpenAI -> Custom -> Pollinations",
        "pollinations": "Free fallback (watermark risk: possible)",
        "gemini": "High quality (requires GEMINI_API_KEY)",
        "openai": "High quality (requires OPENAI_API_KEY)",
        "custom": "OpenAI-compatible endpoint (requires CUSTOM_API_KEY)",
    }
    for name, desc in profiles.items():
        print(f"  {name}: {desc}")


def cmd_styles(args):
    loader = StyleLoader()
    print("Available styles:")
    for s in loader.available_styles():
        preset = loader.load(s)
        desc = preset.get("description", "")
        print(f"  - {s}: {desc}")


def cmd_doctor(args):
    config = Config(args.config)
    _log("AI Handdrawn Toolkit Doctor")
    checks = []
    try:
        import PIL  # noqa
        checks.append(("Pillow", "OK"))
    except Exception:
        checks.append(("Pillow", "MISSING"))
    try:
        import yaml  # noqa
        checks.append(("PyYAML", "OK"))
    except Exception:
        checks.append(("PyYAML", "MISSING"))
    gemini_key = config.get("providers.gemini.api_key")
    checks.append(("Gemini API", "OK" if gemini_key else "NOT CONFIGURED"))
    openai_key = config.get("providers.openai.api_key")
    checks.append(("OpenAI API", "OK" if openai_key else "NOT CONFIGURED"))
    custom_key = config.get("providers.custom.api_key") or os.getenv("CUSTOM_API_KEY")
    checks.append(("Custom API", "OK" if custom_key else "NOT CONFIGURED"))
    try:
        providers = build_providers(config)
        checks.append(("Pollinations", "OK" if providers else "UNAVAILABLE"))
    except Exception as e:
        checks.append(("Pollinations", f"ERROR: {e}"))
    try:
        loader = StyleLoader()
        styles = loader.available_styles()
        checks.append(("Styles", f"OK ({len(styles)} loaded)"))
    except Exception as e:
        checks.append(("Styles", f"ERROR: {e}"))
    for name, status in checks:
        _log(f"  {name}: {status}")
    _log("READY (Pollinations fallback available)")


def main():
    parser = argparse.ArgumentParser(description="AI Handdrawn Toolkit")
    sub = parser.add_subparsers(dest="command")

    p_gen = sub.add_parser("generate", help="Generate a hand-drawn image")
    p_gen.add_argument("prompt", help="Image description")
    p_gen.add_argument("--style", default=None)
    p_gen.add_argument("--provider", default="auto")
    p_gen.add_argument("--width", type=int, default=None)
    p_gen.add_argument("--height", type=int, default=None)
    p_gen.add_argument("--candidates", type=int, default=None)
    p_gen.add_argument("--output", default=None)
    p_gen.add_argument("--output-dir", default=None)
    p_gen.add_argument("--config", default="config.yaml")

    p_prov = sub.add_parser("providers", help="List providers")
    p_prov.add_argument("--config", default="config.yaml")

    p_styles = sub.add_parser("styles", help="List styles")
    p_styles.add_argument("--config", default="config.yaml")

    p_doctor = sub.add_parser("doctor", help="Check environment")
    p_doctor.add_argument("--config", default="config.yaml")

    args = parser.parse_args()
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "providers":
        cmd_providers(args)
    elif args.command == "styles":
        cmd_styles(args)
    elif args.command == "doctor":
        cmd_doctor(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
