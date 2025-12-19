from typing import Iterable, Literal, Optional

import matplotlib.pyplot as plt
import numpy as np

from .config import AxisConfig, GridConfig
from .renderers import Renderer, SeriesSpec, render_line
from .text_utils import draw_text

# デバッグ用に枠を表示する場合は True にする
IS_VISIBLE_FRAME = False


def create_frame(figs) -> None:
    for f in figs:
        ax = f.add_axes([0, 0, 1, 1])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor("none")
        if not IS_VISIBLE_FRAME:
            for spine in ax.spines.values():
                spine.set_visible(False)


def get_pixel_size(fig) -> tuple[int, int]:
    """
    Figure または SubFigure の現在の幅と高さをピクセル単位で返す。
    """
    fig.canvas.draw()
    bbox = fig.bbox
    return bbox.width, bbox.height


def create_fig(width: int = 1280, height: int = 720) -> plt.Figure:
    return plt.figure(figsize=(width / 100, height / 100), dpi=100)


def divide_fig_ratio(fig, direction: Literal["horizontal", "vertical"], ratios: list[float]) -> list[plt.Figure]:
    n_areas = len(ratios)
    if direction == "horizontal":
        figs = fig.subfigures(1, n_areas, width_ratios=ratios, wspace=0, hspace=0)
    else:
        figs = fig.subfigures(n_areas, 1, height_ratios=ratios, wspace=0, hspace=0)
    create_frame(figs)
    return figs


def divide_fig_pixel(fig, direction: Literal["horizontal", "vertical"], sizes: list[Optional[float]]) -> list[plt.Figure]:
    """
    sizes に None が含まれる場合は残余を均等割り当てし、全指定が親を超える場合は例外を投げる。
    """
    parent_width, parent_height = get_pixel_size(fig)
    total_size = parent_width if direction == "horizontal" else parent_height

    n_areas = len(sizes)
    specified_total = sum([s for s in sizes if s is not None])
    if specified_total > total_size:
        raise ValueError("The specified sizes exceed the parent figure size.")
    n_none = sizes.count(None)
    if n_none > 0:
        remaining_size = total_size - specified_total
        size_per_none = remaining_size / n_none
        sizes = [s if s is not None else size_per_none for s in sizes]
    ratios = [s / total_size for s in sizes]

    if direction == "horizontal":
        figs = fig.subfigures(1, n_areas, width_ratios=ratios, wspace=0, hspace=0)
    else:
        figs = fig.subfigures(n_areas, 1, height_ratios=ratios, wspace=0, hspace=0)

    create_frame(figs)
    return figs


def get_padding_subfig(fig, padding: float = 0.1) -> plt.Figure:
    """
    親Figureの中に、指定されたpadding(割合)を空けた新しいSubFigureを作成して返す。
    GridSpecの比率(ratios)を使うことで、constrained_layout環境下でもパディングを死守する。
    """
    gs = fig.add_gridspec(
        3,
        3,
        width_ratios=[padding, 1.0 - 2 * padding, padding],
        height_ratios=[padding, 1.0 - 2 * padding, padding],
        wspace=0,
        hspace=0,
    )

    subfig = fig.add_subfigure(gs[1, 1])
    subfig.set_facecolor("none")
    create_frame([subfig])
    return subfig


def draw_graph_module(fig, title_ratio=0.2, label_ratio=0.1, axis_ratio=0.05) -> list[plt.Figure]:
    parent_width, parent_height = get_pixel_size(fig)
    title_width = int(min(parent_width, parent_height) * title_ratio)
    label_width = int(min(parent_width, parent_height) * label_ratio)
    axis_width = int(min(parent_width, parent_height) * axis_ratio)
    upper, lower = divide_fig_pixel(fig, "vertical", sizes=[None, axis_width + label_width + title_width])
    _, lower, _ = divide_fig_pixel(lower, "horizontal", sizes=[axis_width + label_width, None, axis_width + label_width])
    horizontal_axis, horizontal_label, title = divide_fig_pixel(lower, "vertical", sizes=[axis_width, label_width, title_width])
    vertical_label, vertical_axis, main, _ = divide_fig_pixel(upper, "horizontal", sizes=[label_width, axis_width, None, axis_width + label_width])
    return [horizontal_axis, horizontal_label, vertical_label, vertical_axis, main, title]


def plot_template(title: str = "Modular Subplot Example", *, width: int = 1200, height: int = 800, ratios=[1, 5, 2]) -> tuple[plt.Figure, list[plt.Figure], plt.Figure]:
    fig = create_fig(width=width, height=height)
    figs = divide_fig_ratio(fig, "vertical", ratios=ratios)
    draw_text(figs[0].get_axes()[0], title, mode="fit", fontweight="bold", max_fontsize=36)
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

    ax_h_axis = fig_h_axis.get_axes()[0]
    ax_h_label = fig_h_label.get_axes()[0]
    ax_v_label = fig_v_label.get_axes()[0]
    ax_v_axis = fig_v_axis.get_axes()[0]
    ax_main = fig_main.get_axes()[0]
    ax_title = fig_title.get_axes()[0]

    x_cfg = x_axis
    y_cfg = y_axis
    grid_cfg = grid or GridConfig()
    series_list = list(series_specs) if series_specs is not None else None

    def _minmax(arr: np.ndarray) -> tuple[float, float]:
        return float(np.min(arr)), float(np.max(arr))

    if series_list:
        xs = np.concatenate([np.asarray(spec.x) for spec in series_list])
        ys = np.concatenate([np.asarray(spec.y) for spec in series_list])
        x_min, x_max = _minmax(xs)
        y_min, y_max = _minmax(ys)
    else:
        x_min, x_max = _minmax(np.asarray(x_data))
        y_min, y_max = _minmax(np.asarray(y_data))

    if x_cfg.range is not None:
        x_min, x_max = x_cfg.range
    if y_cfg.range is not None:
        y_min, y_max = y_cfg.range
    x_locator = x_cfg.get_locator()
    y_locator = y_cfg.get_locator()

    ax_main.set_xlim(x_min, x_max)
    ax_main.set_ylim(y_min, y_max)
    ax_main.set_xscale(x_cfg.scale)
    ax_main.set_yscale(y_cfg.scale)

    if grid_cfg.enabled:
        gx_locator = grid_cfg.x_locator or x_locator
        gy_locator = grid_cfg.y_locator or y_locator
        x_ticks_grid = gx_locator.tick_values(x_min, x_max)
        y_ticks_grid = gy_locator.tick_values(y_min, y_max)

        for xt in x_ticks_grid:
            ax_main.axvline(xt, color=grid_cfg.color, linestyle=grid_cfg.linestyle, linewidth=grid_cfg.linewidth, zorder=0)

        for yt in y_ticks_grid:
            ax_main.axhline(yt, color=grid_cfg.color, linestyle=grid_cfg.linestyle, linewidth=grid_cfg.linewidth, zorder=0)

    renderer(ax_main, x_data, y_data)

    for spine in ax_main.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1.0)

    ax_main.set_xticks([])
    ax_main.set_yticks([])

    ax_v_axis.set_ylim(y_min, y_max)
    y_ticks = y_locator.tick_values(y_min, y_max)
    for val in y_ticks:
        label_text = y_cfg.formatter(val) if y_cfg.formatter else f"{val:.1f}"
        draw_text(
            ax_v_axis,
            label_text,
            mode="fixed",
            fontsize=9,
            ha="right",
            va="center",
            x=0.90,
            y=val,
            transform=ax_v_axis.transData,
        )

    ax_h_axis.set_xlim(x_min, x_max)
    x_ticks = x_locator.tick_values(x_min, x_max)
    for val in x_ticks:
        label_text = x_cfg.formatter(val) if x_cfg.formatter else f"{val:.1f}"
        draw_text(
            ax_h_axis,
            label_text,
            mode="fixed",
            fontsize=9,
            ha="center",
            va="top",
            x=val,
            y=0.8,
            transform=ax_h_axis.transData,
        )

    draw_text(ax_v_label, y_cfg.label, mode="fit", rotation=90, fontweight="bold", max_fontsize=20)
    draw_text(ax_h_label, x_cfg.label, mode="fit", fontweight="bold", max_fontsize=20)
    draw_text(ax_title, title, mode="fit", fontweight="bold", fontsize=16, max_fontsize=32)


__all__ = [
    "IS_VISIBLE_FRAME",
    "create_fig",
    "divide_fig_ratio",
    "divide_fig_pixel",
    "get_padding_subfig",
    "draw_graph_module",
    "plot_template",
    "plot_on_module",
]
