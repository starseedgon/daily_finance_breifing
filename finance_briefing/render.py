from __future__ import annotations

from datetime import date
from html import escape
from importlib.resources import files
from string import Template

from .models import Indicator


def _card(item: Indicator) -> str:
    value = "데이터 없음" if item.value is None else f"{item.value:,.2f} {item.unit}".strip()
    change = "—" if item.change_pct is None else f"{item.change_pct:+.2f}%"
    direction = "missing" if item.change_pct is None else ("up" if item.change_pct >= 0 else "down")
    as_of = item.as_of.isoformat() if item.as_of else "—"
    return (
        f'<article class="card {direction}"><h2>{escape(item.label)}</h2>'
        f'<p class="value">{escape(value)}</p><p class="change">{escape(change)}</p>'
        f'<p class="as-of">기준일 {as_of}</p></article>'
    )


def render_briefing(report_date: date, indicators: list[Indicator], provider: str) -> str:
    template = Template(
        files("finance_briefing").joinpath("templates/briefing.html").read_text(encoding="utf-8")
    )
    missing = sum(item.value is None for item in indicators)
    ratio = missing / len(indicators) if indicators else 1.0
    return template.substitute(
        report_date=report_date.isoformat(),
        provider=escape(provider),
        cards="\n".join(_card(item) for item in indicators),
        missing_ratio=f"{ratio:.1%}",
    )
