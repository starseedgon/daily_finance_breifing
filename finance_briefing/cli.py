from __future__ import annotations

import argparse
import json
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
    missing = sum(item.value is None for item in indicators)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    daily_dir = args.output_dir / f"{report_date:%Y/%m}"
    daily_dir.mkdir(parents=True, exist_ok=True)
    stem = f"market-summary-{report_date.isoformat()}"
    dated = daily_dir / f"{stem}.html"
    dated.write_text(render_briefing(report_date, indicators, args.provider), encoding="utf-8")
    data_file = daily_dir / f"{stem}.json"
    data_file.write_text(
        json.dumps(
            {
                "report_date": report_date.isoformat(),
                "provider": args.provider,
                "indicators": [
                    {
                        "key": item.key,
                        "label": item.label,
                        "value": item.value,
                        "change_pct": item.change_pct,
                        "as_of": item.as_of.isoformat() if item.as_of else None,
                        "unit": item.unit,
                    }
                    for item in indicators
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = daily_dir / f"run-manifest-{report_date.isoformat()}.json"
    manifest.write_text(
        json.dumps(
            {
                "started_at": started,
                "report_date": report_date.isoformat(),
                "provider": args.provider,
                "missing_count": missing,
                "indicator_count": len(indicators),
                "html": dated.relative_to(args.output_dir).as_posix(),
                "json": data_file.relative_to(args.output_dir).as_posix(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    shutil.copyfile(dated, args.output_dir / "latest.html")
    shutil.copyfile(dated, args.output_dir / "index.html")
    for item in indicators:
        logging.info("indicator=%s as_of=%s missing=%s", item.key, item.as_of, item.value is None)
    logging.info(
        "started_at=%s report_date=%s missing_ratio=%.3f output=%s",
        started, report_date, missing / len(indicators) if indicators else 1.0, dated,
    )
    return 0
