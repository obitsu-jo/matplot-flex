from pathlib import Path

import numpy as np
from matplot_flex import (
    AxisConfig,
    LegendConfig,
    SeriesSpec,
    divide_fig_ratio,
    draw_graph_module,
    draw_rounded_frame,
    draw_text,
    format_params,
    get_padding_subfig,
    get_primary_axes,
    plot_on_module,
    plot_template,
    render_line,
    render_multi,
    render_scatter,
)


def main(output_path: str | Path = "modular_subplot_example.png"):
    fig, figs = plot_template("Subplot Module Example")

    # 図本体部分 > [左図, 右図]
    main_figs = divide_fig_ratio(figs[1], "horizontal", ratios=[1, 1])

    # ダミーデータの作成
    x = np.linspace(0, 10, 100)
    y_sin = np.sin(x)
    y_cos = np.cos(x)

    # 左側: sin と cos の重ね書きサンプル
    module = draw_graph_module(main_figs[0])
    series = [
        SeriesSpec(x=x, y=y_sin, renderer=render_line, label="sin", color="tab:blue", linewidth=2.2),
        SeriesSpec(x=x, y=y_cos, renderer=render_line, label="cos", color="tab:orange", linewidth=2.2, linestyle="--"),
    ]
    legend_conf = LegendConfig(loc="upper right", frameon=True)
    y_range = (min(np.min(y_sin), np.min(y_cos)), max(np.max(y_sin), np.max(y_cos)))
    import matplotlib.ticker as mticker

    y_axis_config = AxisConfig(label="value", range=y_range, locator=mticker.FixedLocator(np.linspace(-1, 1, 5)))
    plot_on_module(
        module,
        x,
        y_sin,
        "Sine & Cosine",
        renderer=lambda ax, xx, yy: render_multi(ax, series, legend=legend_conf),
        x_axis=AxisConfig(label="x"),
        y_axis=y_axis_config,
        series_specs=series,
    )

    # 右側: 従来の単系列描画（散布図）
    module = draw_graph_module(main_figs[1])
    y_axis_config.label = "amplitude"
    plot_on_module(
        module,
        x,
        y_sin,
        "Sine Wave Scatter",
        renderer=render_scatter,
        x_axis=AxisConfig(label="Wave"),
        y_axis=y_axis_config,
    )

    # メタデータ部分 > [数式, パラメータ]
    meta_figs = divide_fig_ratio(figs[2], "horizontal", ratios=[1, 1])
    math_fig, parameter_fig = meta_figs
    math_fig = get_padding_subfig(math_fig, padding=0.1)
    draw_rounded_frame(math_fig)
    draw_text(
        get_primary_axes(math_fig),
        "Equation:\n" r"$y = a\sin(bx)$" + "\n" r"$y = a\cos(bx)$",
        mode="fit",
        fontweight="bold",
        max_fontsize=22,
    )

    params = {"a": 1.0, "b": 0.5}
    param_str = format_params(params)
    parameter_fig = get_padding_subfig(parameter_fig, padding=0.1)
    draw_rounded_frame(parameter_fig)
    draw_text(get_primary_axes(parameter_fig), param_str, mode="fit", max_fontsize=24)

    out_path = Path(output_path)
    fig.savefig(out_path, dpi=220)
    print("Plotting completed.")


if __name__ == "__main__":
    main()
