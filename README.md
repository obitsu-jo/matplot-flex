# Matplot Flex

Reusable Matplotlib helpers for modular subplot layouts, text fitting, and common renderers.

## Structure
- `matplot_flex/config.py`: Axis/legend/grid configs.
- `matplot_flex/text_utils.py`: Text fitting, param formatter, rounded frames, date/sci formatters.
- `matplot_flex/renderers.py`: Line/scatter/bar renderers, multi-series helper, `SeriesSpec`.
- `matplot_flex/layout.py`: Figure/subfigure builders and `plot_on_module` orchestration.
- `main.py`: Example that generates `modular_subplot_example.png`.
- `smoke_test.py`: Simple generation check.

All public symbols are re-exported from `matplot_flex/__init__.py`.  
More detailed API notes: see `matplot_flex/README.md`.

## Quick start
```python
import numpy as np
from matplot_flex import (
    AxisConfig, LegendConfig, SeriesSpec,
    plot_template, divide_fig_ratio, draw_graph_module, plot_on_module,
    render_line, render_multi,
)

fig, figs = plot_template("My Plot")
left_fig, right_fig = divide_fig_ratio(figs[1], "horizontal", ratios=[1, 1])

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
series = [
    SeriesSpec(x=x, y=y1, renderer=render_line, label="sin"),
    SeriesSpec(x=x, y=y2, renderer=render_line, label="cos", linestyle="--"),
]

plot_on_module(
    draw_graph_module(left_fig),
    x,
    y1,
    "Sine & Cosine",
    renderer=lambda ax, xx, yy: render_multi(ax, series, legend=LegendConfig()),
    x_axis=AxisConfig(label="x"),
    y_axis=AxisConfig(label="value"),
    series_specs=series,  # ensures axes cover all series
)

fig.savefig("example.png", dpi=220)
```

## Run the bundled example
```
python main.py
```
Outputs `modular_subplot_example.png` in the repo root.

## Smoke test
```
python smoke_test.py
```
Regenerates the PNG and asserts it exists.

## Install as a local package (recommended for reuse)
```
pip install -e .
```
After that you can `import matplot_flex` from other directories in the same environment.
