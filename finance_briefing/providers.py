from __future__ import annotations

from datetime import date, timedelta
from typing import Protocol

from .models import Indicator


class Provider(Protocol):
    def fetch(self, target_date: date) -> list[Indicator]: ...


class FixtureProvider:
    """Stable, network-free sample data used by default and in tests."""

    def fetch(self, target_date: date) -> list[Indicator]:
        return [
            Indicator("kospi", "KOSPI", 2697.23, 0.83, target_date, "pt"),
            Indicator("kosdaq", "KOSDAQ", 786.33, -0.15, target_date, "pt"),
            Indicator("usdkrw", "USD/KRW", 1358.40, 0.21, target_date, "원"),
            Indicator("sp500", "S&P 500", 5543.22, 0.54, target_date, "pt"),
        ]


class FinanceDataReaderProvider:
    SYMBOLS = (
        ("kospi", "KOSPI", "KS11", "pt"),
        ("kosdaq", "KOSDAQ", "KQ11", "pt"),
        ("usdkrw", "USD/KRW", "USD/KRW", "원"),
        ("sp500", "S&P 500", "US500", "pt"),
    )

    def fetch(self, target_date: date) -> list[Indicator]:
        try:
            import FinanceDataReader as fdr
        except ImportError as exc:
            raise RuntimeError(
                "fdr provider requires: python -m pip install -e '.[live]'"
            ) from exc

        start = target_date - timedelta(days=10)
        results: list[Indicator] = []
        for key, label, symbol, unit in self.SYMBOLS:
            try:
                frame = fdr.DataReader(symbol, start.isoformat(), target_date.isoformat())
                frame = frame.loc[frame.index.date <= target_date]
                closes = frame["Close"].dropna()
                if closes.empty:
                    raise ValueError("no close price")
                value = float(closes.iloc[-1])
                change = (
                    (value / float(closes.iloc[-2]) - 1) * 100
                    if len(closes) >= 2
                    else None
                )
                as_of = closes.index[-1].date()
                results.append(Indicator(key, label, value, change, as_of, unit))
            except Exception:
                results.append(Indicator(key, label, None, None, None, unit))
        return results


def get_provider(name: str) -> Provider:
    if name == "fixture":
        return FixtureProvider()
    if name == "fdr":
        return FinanceDataReaderProvider()
    raise ValueError(f"unknown provider: {name}")
