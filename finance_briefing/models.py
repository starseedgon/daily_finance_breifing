from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Indicator:
    key: str
    label: str
    value: float | None
    change_pct: float | None
    as_of: date | None
    unit: str = ""
