"""CLI entrypoint using argparse."""
import argparse
import sys
import json
from app.core.config import Config
from app.core.router import resolve_provider, build_providers
from app.core.prompt_compiler import PromptCompiler
from app.styles.loader import StyleLoader
from app.quality.heuristic import score as heuristic_score
from app.quality.watermark import is_watermarked
from app.quality.style_gate import check_style_gate
from app.quality.vision_judge import judge_with_gemini
from app.core.errors import HanddrawnError, ErrorCode


def _print_candidate(idx, status, reason, score=None):
    if status == "PASS":
        mark = "✓ PASS"
    elif status == "REJECT":
        mark = "✗ REJECT"
    else:
        mark = "? REVIEW"
    line = f"Candidate #{idx}  {mark}"
    if reason:
        line += f"  {reason}"
    if score is not None:
        line += f"  score: {score:.1f}"
    print(f"  {line}")


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
            # Only retry on transient errors
            if e.code in (ErrorCode.NETWORK_ERROR, ErrorCode.TIMEOUT, ErrorCode.RATE_LIMIT, ErrorCode.PROVIDER_ERROR):
                continue
            raise
        except Exception as e:
            last_error = e
            continue
    raise last_error or HanddrawnError(ErrorCode.PROVIDER_ERROR, "Generation failed after retries.")


def cmd_generate(args):
    config = Config(args.config)
    compiler = PromptCompiler(StyleLoader())
    style = args.style or config.default_style
    positive, negative = compiler.compile(args.prompt, style=style)
    providers = resolve_provider(args.provider, config)

    width = args.width or config.width
    height = args.height or config.height
    candidates_needed = args.candidates or config.candidates
    max_rounds = 2

    vision_key = config.get("providers.gemini.api_key")

    results = []
    rejections = []
    round_num = 0
    while len(results) < candidates_needed and round_num < max_rounds:
        round_num += 1
        for provider in providers:
            try:
                imgs = _generate_with_retry(provider, positive, negative, width, height)
            except HanddrawnError as e:
                print(f"⚠️  {provider.name} failed: {e.message}")
                if e.suggestion:
                    print(f"   Suggestion: {e.suggestion}")
                continue
            except Exception as e:
                print(f"⚠️  {provider.name} unexpected error: {e}")
                continue

            for img in imgs:
                idx = len(results) + len(rejections) + 1

                # Gate 0: file integrity
                if len(img.data) < 1000:
                    rejections.append({"candidate": idx, "reason": "INVALID_IMAGE"})
                    _print_candidate(idx, "REJECT", "INVALID_IMAGE")
                    continue

                # Gate 1: watermark
                wm, wm_detail = is_watermarked(img.data, vision_api_key=vision_key)
                if wm:
                    reason = "PROVIDER_WATERMARK"
                    rejections.append({"candidate": idx, "reason": reason, "detail": wm_detail})
                    _print_candidate(idx, "REJECT", reason)
                    continue

                # Gate 2: style mismatch
                style_check = check_style_gate(style, positive)
                if not style_check["pass"]:
                    reason = f"STYLE_MISMATCH ({', '.join(style_check['violations'][:3])})"
                    rejections.append({"candidate": idx, "reason": reason})
                    _print_candidate(idx, "REJECT", reason)
                    continue

                # Gate 3: rendering mismatch (heuristic)
                try:
                    q = heuristic_score(img.data)
                except Exception:
                    q = {"final_score": 0.0}
                if q["final_score"] < 0.35:
                    reason = "RENDERING_MISMATCH"
                    rejections.append({"candidate": idx, "reason": reason})
                    _print_candidate(idx, "REJECT", reason)
                    continue

                # Pass
                results.append((img, q))
                _print_candidate(idx, "PASS", "OK", q.get("final_score", 0) * 10)
                if len(results) >= candidates_needed:
                    break
            if len(results) >= candidates_needed:
                break

    if not results:
        print("❌ All candidates rejected. Run `python -m app.cli doctor` to check config.")
        sys.exit(1)

    # Select winner
    if len(results) == 1:
        best_img, best_q = results[0]
        best_score = best_q.get("final_score", 0) * 10
        print(f"\n✓ Selected best candidate (auto, only candidate)")
    else:
        scored = []
        for img, q in results:
            scored.append((q.get("final_score", 0) * 10, img, q))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_img, best_meta = scored[0]
        print("\nCandidate scores:")
        for idx, (sc, img, meta) in enumerate(scored, 1):
            print(f"  Candidate #{idx}  {sc:.1f}/10")
        print(f"\n✓ Selected best candidate ({best_score:.1f}/10)")

    # Optional refinement if score < 7.8
    refined = False
    if best_score < 7.8 and vision_key:
        print("⚠️  Best score < 7.8, attempting one-pass refinement...")
        try:
            refined_prompt = (
                positive
                + ", confident graphite/fine-ink contours, natural line-weight variation, "
                "reduce painterly color, reduce digital gloss, simplify background, "
                "keep subject recognizable, do not add text or logos"
            )
            refined_imgs = _generate_with_retry(
                best_img, refined_prompt, negative, width, height
            )
            if refined_imgs:
                refined_img = refined_imgs[0]
                wm2, _ = is_watermarked(refined_img.data, vision_api_key=vision_key)
                if not wm2:
                    best_img = refined_img
                    refined = True
                    print("✓ Refinement succeeded")
                else:
                    print("✗ Refinement produced watermark, keeping original")
        except Exception as e:
            print(f"✗ Refinement failed: {e}")

    out = args.output or f"generated/{style}_{hash(args.prompt) % 10000}.png"
    with open(out, "wb") as f:
        f.write(best_img.data)
    print(f"Saved: {out}")
    print(f"Provider: {best_img.provider} | Model: {best_img.model}")

    # Output metadata
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
    meta_path = out.rsplit(".", 1)[0] + ".json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"Metadata: {meta_path}")


def cmd_providers(args):
    config = Config(args.config)
    print("Available providers:")
    profiles = {
        "auto": "Gemini → OpenAI → FLUX → Pollinations",
        "pollinations": "Free fallback (watermark risk: possible)",
        "gemini": "High quality (requires GEMINI_API_KEY)",
        "openai": "High quality (requires OPENAI_API_KEY)",
        "flux": "Not implemented yet",
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
    print("AI Handdrawn Toolkit Doctor\n")
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
        print(f"  {name}: {status}")
    print("\nREADY (Pollinations fallback available)")


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
    p_gen.add_argument("--config", default="config.yaml")

    p_prov = sub.add_parser("providers", help="List providers")
    p_prov.add_argument("--config", default="config.yaml")

    p_styles = sub.add_parser("styles", help="List styles")

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
