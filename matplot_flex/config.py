from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import matplotlib.ticker as mticker


@dataclass
class AxisConfig:
    label: str = ""
    range: Optional[tuple[float, float]] = None
    scale: str = "linear"  # 'linear' | 'log' | etc.
    formatter: Optional[Callable[[float], str]] = None
    locator: Optional[mticker.Locator] = None
    ticks: Optional[tuple[str, Any]] = ("nbins", 5)  # ("nbins", n) | ("interval", step) | ("values", list) | ("auto", None)

    def get_locator(self) -> mticker.Locator:
        if self.locator is not None:
            return self.locator
        if self.ticks is None:
            return mticker.MaxNLocator(nbins=5)
        kind, value = self.ticks
        if kind == "nbins":
            return mticker.MaxNLocator(nbins=value)
        if kind == "interval":
            return mticker.MultipleLocator(value)
        if kind == "values":
            return mticker.FixedLocator(value)
        if kind == "auto":
            return mticker.AutoLocator()
        return mticker.MaxNLocator(nbins=5)


@dataclass
class GridConfig:
    enabled: bool = True
    color: str = "lightgray"
    linestyle: str = "--"
    linewidth: float = 0.8
    x_locator: Optional[mticker.Locator] = None
    y_locator: Optional[mticker.Locator] = None


@dataclass
class LegendConfig:
    enabled: bool = True
    loc: str = "best"
    ncol: int = 1
    frameon: bool = True
    fontsize: Optional[float] = None
    kwargs: dict[str, Any] = field(default_factory=dict)

    def to_kwargs(self) -> dict[str, Any]:
        merged = dict(self.kwargs)
        merged.setdefault("loc", self.loc)
        merged.setdefault("ncol", self.ncol)
        merged.setdefault("frameon", self.frameon)
        if self.fontsize is not None:
            merged.setdefault("fontsize", self.fontsize)
        return merged


__all__ = ["AxisConfig", "GridConfig", "LegendConfig"]
