from __future__ import annotations

import argparse
import logging
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

from .providers import get_provider
from .render import render_briefing


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a daily finance briefing")
    parser.add_argument("--provider", choices=("fixture", "fdr"), default="fixture")
    parser.add_argument("--date", type=date.fromisoformat, dest="report_date")
    parser.add_argument("--output-dir", type=Path, default=Path("public"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report_date = args.report_date or datetime.now(timezone.utc).date()
    started = datetime.now(timezone.utc).isoformat()
    indicators = get_provider(args.provider).fetch(report_date)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    dated = args.output_dir / f"{report_date.isoformat()}.html"
    dated.write_text(render_briefing(report_date, indicators, args.provider), encoding="utf-8")
    shutil.copyfile(dated, args.output_dir / "latest.html")
    shutil.copyfile(dated, args.output_dir / "index.html")
    missing = sum(item.value is None for item in indicators)
    for item in indicators:
        logging.info("indicator=%s as_of=%s missing=%s", item.key, item.as_of, item.value is None)
    logging.info(
        "started_at=%s report_date=%s missing_ratio=%.3f output=%s",
        started, report_date, missing / len(indicators) if indicators else 1.0, dated,
    )
    return 0
