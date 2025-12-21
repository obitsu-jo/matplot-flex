from typing import Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np

from .axes_utils import get_primary_axes
from .config import AxisConfig, GridConfig
from .decorators import (
    apply_axis_limits,
    draw_axis_labels,
    draw_axis_tick_labels,
    draw_grid,
    draw_title,
    hide_main_ticks,
    style_main_spines,
)
from .layout import create_fig, divide_fig_ratio
from .renderers import Renderer, SeriesSpec, render_line
from .text_utils import draw_text


def _minmax(arr: np.ndarray) -> tuple[float, float]:
    return float(np.min(arr)), float(np.max(arr))


def _resolve_data_range(
    x_data: np.ndarray,
    y_data: np.ndarray,
    series_specs: Optional[Iterable[SeriesSpec]],
) -> tuple[float, float, float, float]:
    series_list = list(series_specs) if series_specs is not None else None
    if series_list:
        xs = np.concatenate([np.asarray(spec.x) for spec in series_list])
        ys = np.concatenate([np.asarray(spec.y) for spec in series_list])
        x_min, x_max = _minmax(xs)
        y_min, y_max = _minmax(ys)
    else:
        x_min, x_max = _minmax(np.asarray(x_data))
        y_min, y_max = _minmax(np.asarray(y_data))
    return x_min, x_max, y_min, y_max


def plot_template(
    title: str = "Modular Subplot Example",
    *,
    width: int = 1200,
    height: int = 800,
    ratios: Optional[list[float]] = None,
) -> tuple[plt.Figure, list[plt.Figure]]:
    fig = create_fig(width=width, height=height)
    if ratios is None:
        ratios = [1, 5, 2]
    figs = divide_fig_ratio(fig, "vertical", ratios=ratios)
    ax_title = get_primary_axes(figs[0], hide_axis_on_create=True)
    draw_text(ax_title, title, mode="fit", fontweight="bold", max_fontsize=36)
    return fig, figs


def plot_on_module(
    module_figs: list[plt.Figure],
    x_data: np.ndarray,
    y_data: np.ndarray,
    title: str,
    *,
    renderer: Renderer = render_line,
    x_axis: AxisConfig,
    y_axis: AxisConfig,
    grid: Optional[GridConfig] = None,
    series_specs: Optional[Iterable[SeriesSpec]] = None,
) -> None:
    """
    作成したモジュール構造(figsリスト)に対して、データと装飾を流し込む関数。
    """
    fig_h_axis, fig_h_label, fig_v_label, fig_v_axis, fig_main, fig_title = module_figs

    ax_h_axis = get_primary_axes(fig_h_axis, hide_axis_on_create=True)
    ax_h_label = get_primary_axes(fig_h_label, hide_axis_on_create=True)
    ax_v_label = get_primary_axes(fig_v_label, hide_axis_on_create=True)
    ax_v_axis = get_primary_axes(fig_v_axis, hide_axis_on_create=True)
    ax_main = get_primary_axes(fig_main)
    ax_title = get_primary_axes(fig_title, hide_axis_on_create=True)

    x_cfg = x_axis
    y_cfg = y_axis
    grid_cfg = grid or GridConfig()

    x_min, x_max, y_min, y_max = _resolve_data_range(x_data, y_data, series_specs)

    if x_cfg.range is not None:
        x_min, x_max = x_cfg.range
    if y_cfg.range is not None:
        y_min, y_max = y_cfg.range

    x_locator = x_cfg.get_locator()
    y_locator = y_cfg.get_locator()

    apply_axis_limits(ax_main, x_cfg, y_cfg, x_min, x_max, y_min, y_max)
    draw_grid(ax_main, x_min, x_max, y_min, y_max, grid_cfg, x_locator, y_locator)
    renderer(ax_main, x_data, y_data)
    style_main_spines(ax_main)
    hide_main_ticks(ax_main)

    draw_axis_tick_labels(ax_h_axis, ax_v_axis, x_cfg, y_cfg, x_min, x_max, y_min, y_max, x_locator, y_locator)
    draw_axis_labels(ax_h_label, ax_v_label, x_cfg, y_cfg)
    draw_title(ax_title, title)


__all__ = ["plot_template", "plot_on_module"]
