import io
from datetime import datetime, timedelta

import matplotlib

# GUI不要で描画できるようにAggを使用
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from matplot_flex import (
    AxisConfig,
    LegendConfig,
    SeriesSpec,
    date_formatter,
    draw_graph_module,
    plot_on_module,
    plot_template,
    render_bar,
    render_line,
    render_multi,
)


def _render_to_buffer(fig) -> None:
    buf = io.BytesIO()
    fig.savefig(buf, format="png")


def test_multi_series_line() -> None:
    fig, figs = plot_template("multi-series")
    module_figs = draw_graph_module(figs[1])
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    series = [
        SeriesSpec(x=x, y=y1, renderer=render_line, label="sin"),
        SeriesSpec(x=x, y=y2, renderer=render_line, label="cos", linestyle="--"),
    ]
    plot_on_module(
        module_figs,
        x,
        y1,
        "Sine & Cosine",
        renderer=lambda ax, xx, yy: render_multi(ax, series, legend=LegendConfig()),
        x_axis=AxisConfig(label="x"),
        y_axis=AxisConfig(label="value"),
        series_specs=series,
    )
    _render_to_buffer(fig)
    plt.close(fig)


def test_bar_default_width() -> None:
    fig, figs = plot_template("bar")
    module_figs = draw_graph_module(figs[1])
    x = np.array([0.0, 0.5, 2.0, 3.5])
    y = np.array([1.0, 2.5, 1.5, 3.0])
    plot_on_module(
        module_figs,
        x,
        y,
        "Bar",
        renderer=render_bar,
        x_axis=AxisConfig(label="x"),
        y_axis=AxisConfig(label="value"),
    )
    _render_to_buffer(fig)
    plt.close(fig)


def test_date_axis_formatter() -> None:
    fig, figs = plot_template("date-axis")
    module_figs = draw_graph_module(figs[1])
    base = datetime(2025, 1, 1)
    dates = [base + timedelta(days=delta) for delta in range(5)]
    x = mdates.date2num(dates)
    y = np.array([0.5, 1.2, 0.9, 1.5, 1.1])
    plot_on_module(
        module_figs,
        x,
        y,
        "Date Axis",
        renderer=render_line,
        x_axis=AxisConfig(label="date", formatter=date_formatter("%Y-%m-%d"), ticks=("nbins", 4)),
        y_axis=AxisConfig(label="value"),
    )
    _render_to_buffer(fig)
    plt.close(fig)
