# matplot_flex package guide (detailed)

Matplotlib 補助を用途別に分割したパッケージです。`from matplot_flex import ...` で主要APIをまとめて取り出せます。

## モジュール別の役割と主なAPI

### config.py
- `AxisConfig(label="", range=None, scale="linear", formatter=None, locator=None, ticks=("nbins", 5))`
  - `range` 未指定ならデータから min/max を自動決定。`series_specs` を渡した場合は全系列を対象に計算。
  - `ticks`: `"nbins"`, `"interval"`, `"values"`, `"auto"`, または `None`（MaxNLocator）。`locator` 指定があればそちらを優先。
  - `scale`: `"linear"` / `"log"` などを `ax.set_{x,y}scale` に渡す。
- `GridConfig(enabled=True, color="lightgray", linestyle="--", linewidth=0.8, x_locator=None, y_locator=None)`
  - `plot_on_module` でグリッド描画時に使用。Locator 未指定なら軸と同じものを利用。
- `LegendConfig(enabled=True, loc="best", ncol=1, frameon=True, fontsize=None, kwargs=None)`
  - `to_kwargs()` で `ax.legend` にそのまま渡せる dict を生成。

### axes_utils.py
- `get_primary_axes(fig, hide_axis_on_create=False)`
  - Figure/SubFigure の主Axesを取得する。無ければ作成する。
  - `hide_axis_on_create=True` の場合のみ、生成直後のAxesを `axis off` にする。

### renderers.py
- 単系列レンダラー: `render_line`, `render_scatter`, `render_bar`
  - `render_bar` は幅未指定でもデータ間隔から 0.8 倍を推定（非等間隔・1点でも安全）。
- 複数系列:
  - `SeriesSpec(x, y, renderer=render_line, label=None, color=None, linestyle=None, marker=None, linewidth=None, kwargs=None)`
    - 長さ不一致なら例外。`to_kwargs` で描画引数を生成。
  - `render_multi(ax, series_specs, legend=None, use_color_cycle=True)`
    - ラベル付きなら凡例を描画。色は rcParams のサイクルを優先し、なければデフォルトカラーを使用。

### text_utils.py
- `draw_text(ax, text, mode="fit"|"fixed", ...)`
  - `mode="fit"` で枠（デフォルトは Axes 全体）に収まるようフォントサイズを自動調整。`target_bbox` で合わせ先を変更可能。
- `draw_rounded_frame(fig, bg_color="#eeeeee", edge_color="black")`
  - SubFigure/Figure 全体に角丸背景を敷く。
- `format_params(dict)`
  - パラメータ表示用の数式表記文字列を生成。
- フォーマッタ: `sci_formatter(decimals=1)`, `date_formatter(fmt="%Y-%m-%d")`

### layout.py
- レイアウト作成:
  - `create_fig(width=1280, height=720)`
  - `divide_fig_ratio(fig, direction, ratios)` / `divide_fig_pixel(fig, direction, sizes)`
  - `get_padding_subfig(fig, padding=0.1)`
  - `draw_graph_module(fig)`: 目盛・ラベル・タイトル・メイン領域をまとめた `GraphModule` を返す。
    - `x_axis`, `x_label`, `y_label`, `y_axis`, `main`, `title`
- デバッグ: `IS_VISIBLE_FRAME` を True にすると分割枠を表示。

### decorators.py
- 目盛・ラベル・グリッド・タイトルの装飾処理をまとめる。
  - 軸/目盛ラベル描画、グリッド描画、主軸の外観調整など。

### templates.py
- `plot_template(title, width=1200, height=800, ratios=None)`
  - タイトル/メイン/メタの 3 分割を `(fig, figs)` で返す（`ratios=None` の場合は `[1, 5, 2]`）。
- 中央の司令塔:
  - `plot_on_module(module, x_data, y_data, title, renderer=render_line, x_axis, y_axis, grid=None, series_specs=None)`
    - 軸レンジは `series_specs` があれば全系列から計算し、`AxisConfig.range` 指定があればそれを優先。
    - グリッドはデータより背面 (`zorder=0`) に描画し、目盛・ラベル・タイトルを各サブ領域に配置。

## 典型的な使い方の流れ
```python
from matplot_flex import (
    AxisConfig, LegendConfig, SeriesSpec,
    plot_template, divide_fig_ratio, draw_graph_module, plot_on_module,
    render_line, render_multi,
)
import numpy as np

fig, figs = plot_template("My Plot")
left_fig, right_fig = divide_fig_ratio(figs[1], "horizontal", [1, 1])

x = np.linspace(0, 10, 200)
series = [
    SeriesSpec(x=x, y=np.sin(x), renderer=render_line, label="sin"),
    SeriesSpec(x=x, y=np.cos(x), renderer=render_line, label="cos", linestyle="--"),
]

module = draw_graph_module(left_fig)
plot_on_module(
    module,
    x,
    series[0].y,
    "Sine & Cosine",
    renderer=lambda ax, xx, yy: render_multi(ax, series, legend=LegendConfig()),
    x_axis=AxisConfig(label="x"),
    y_axis=AxisConfig(label="value"),
    series_specs=series,  # 複数系列の範囲をカバー
)
fig.savefig("example.png", dpi=220)
```

## レイアウトのカスタムヒント
- ピクセル指定で割りたいときは `divide_fig_pixel`。`None` を含めると残余を均等配分、総和が親を超えると例外。
- 余白を確保して内側に描きたいときは `get_padding_subfig` を使用。
- 目盛密度を調整したいときは `AxisConfig.ticks` を `"interval"` や `"values"` にする。例: `AxisConfig(ticks=("interval", 0.5))`。
- グリッドだけ別 Locator にしたいときは `GridConfig(x_locator=..., y_locator=...)` を渡す。

## よくある落とし穴と対策
- 複数系列描画では必ず `series_specs` を `plot_on_module` に渡して軸範囲を全系列で計算させる。
- 棒幅が合わないときは `render_bar(..., width=明示値)` を指定する。
- 目盛文字が重なる場合は `AxisConfig.ticks` で本数を減らすか、`draw_text` の `fontsize` を小さめに。
- 背景透過を維持したい場合は SubFigure の facecolor が `"none"` になっていることを確認（`get_padding_subfig` は既定で透明）。

## テスト / 実行
- サンプル: `python main.py` → `modular_subplot_example.png` を生成。
- スモークテスト: `python smoke_test.py` → PNG 生成を確認。
