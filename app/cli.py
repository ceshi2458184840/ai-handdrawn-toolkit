"""CLI entrypoint using argparse."""
import argparse
import sys
from app.core.config import Config
from app.core.router import resolve_provider, build_providers
from app.core.prompt_compiler import PromptCompiler
from app.styles.loader import StyleLoader
from app.quality.heuristic import score
from app.core.errors import HanddrawnError, ErrorCode


def cmd_generate(args):
    config = Config(args.config)
    compiler = PromptCompiler(StyleLoader())
    style = args.style or config.default_style
    positive, negative = compiler.compile(args.prompt, style=style)
    providers = resolve_provider(args.provider, config)

    width = args.width or config.width
    height = args.height or config.height
    candidates = args.candidates or config.candidates

    results = []
    for provider in providers:
        try:
            imgs = provider.generate(
                positive,
                negative_prompt=negative,
                width=width,
                height=height,
            )
            results.extend(imgs)
            if len(results) >= candidates:
                break
        except HanddrawnError as e:
            print(f"⚠️  {provider.name} failed: {e.message}")
            if e.suggestion:
                print(f"   Suggestion: {e.suggestion}")
            continue
        except Exception as e:
            print(f"⚠️  {provider.name} unexpected error: {e}")
            continue

    if not results:
        print("❌ All providers failed. Run `python -m app.cli doctor` to check config.")
        sys.exit(1)

    best = results[0]
    if len(results) > 1:
        scored = []
        for img in results:
            try:
                s = score(img.data)
                scored.append((s["final_score"], img, s))
            except Exception:
                scored.append((0.0, img, {}))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best, best_meta = scored[0]
        print("\nCandidate scores:")
        for idx, (sc, img, meta) in enumerate(scored, 1):
            print(f"  Candidate #{idx}  {sc:.2f}/10")
        print(f"\n✓ Selected best candidate ({best_score:.2f}/10)")
    else:
        print("\n✓ Generated 1 candidate")

    out = args.output or f"generated/{style}_{hash(args.prompt) % 10000}.png"
    with open(out, "wb") as f:
        f.write(best.data)
    print(f"Saved: {out}")
    print(f"Provider: {best.provider} | Model: {best.model}")


def cmd_providers(args):
    config = Config(args.config)
    print("Available providers:")
    for name in ["auto", "pollinations", "gemini", "openai", "flux"]:
        status = "enabled" if name in ["auto", "pollinations"] else "config required"
        print(f"  {name}: {status}")


def cmd_styles(args):
    loader = StyleLoader()
    print("Available styles:")
    for s in loader.available_styles():
        print(f"  - {s}")


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
    has_provider = gemini_key or openai_key
    if all(s in ("OK",) or s.startswith("OK (") or s == "OK" for _, s in checks) and has_provider:
        print("\nREADY")
    else:
        print("\nREADY (Pollinations fallback available)" if not has_provider else "\nISSUES FOUND")


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
