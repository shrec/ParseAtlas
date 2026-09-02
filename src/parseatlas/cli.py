"""Command-line interface for ParseAtlas experiments."""

import argparse
import sys

from .analyze import analyze_expression, to_json, to_markdown
from .functions import OUTER_FUNCTIONS, analyze_outer_functions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="parseatlas")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("expression")
    analyze.add_argument("--format", choices=("json", "markdown"), default="json")
    analyze.add_argument("--outer", nargs="*", choices=tuple(OUTER_FUNCTIONS), help="Analyze the inner expression under outer functions")
    args = parser.parse_args(argv)
    if args.command == "analyze":
        report = analyze_expression(args.expression)
        if args.outer is not None:
            report["outer_functions"] = analyze_outer_functions(args.expression, args.outer or tuple(OUTER_FUNCTIONS))
        output = to_json(report) if args.format == "json" else to_markdown(report)
        sys.stdout.write(output)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
