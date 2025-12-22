# matplot-flex 全体仕様書（AI向け完全版）

この文書は本リポジトリの機能を漏れなく把握するための詳細仕様です。実装の挙動に基づき、すべての関数・クラスの引数、戻り値、処理内容、例外や注意点を記載します。

## 目的と対象

- 対象: `matplot_flex/` パッケージと付随スクリプト（`main.py`, `smoke_test.py`）
- 目的: 仕様の完全把握と自動利用（AIによる理解含む）
- 範囲外: 外部ライブラリの内部実装（Matplotlib/NumPy）

## 前提環境・依存

- Python 3.10 以上
- 依存（範囲）: `matplotlib>=3.8,<4`, `numpy>=1.26,<2`
- ヘッドレス実行時は `matplotlib.use("Agg")` を推奨（`smoke_test.py` で実施済み）

## 公開API（`matplot_flex/__init__.py` で再エクスポート）

- `AxisConfig`, `GridConfig`, `LegendConfig`
- `get_primary_axes`
- `Renderer`, `SeriesSpec`
- `render_line`, `render_scatter`, `render_bar`, `render_multi`
- `draw_text`, `draw_rounded_frame`, `format_params`, `sci_formatter`, `date_formatter`
- `IS_VISIBLE_FRAME`
- `GraphModule`
- `create_fig`, `divide_fig_ratio`, `divide_fig_pixel`, `get_padding_subfig`
- `draw_graph_module`, `plot_template`, `plot_on_module`

## モジュール別の詳細

### `matplot_flex/config.py`

#### `AxisConfig`（dataclass）

**フィールド**
- `label: str = ""`  
  軸ラベル文字列。
- `range: Optional[tuple[float, float]] = None`  
  使う場合は（min, max）を固定する。未指定ならデータから算出。
- `scale: str = "linear"`  
  `"linear"`, `"log"` 等を `ax.set_{x,y}scale` に渡す。
- `formatter: Optional[Callable[[float], str]] = None`  
  目盛ラベル文字列を作る関数。未指定なら `"{val:.1f}"`。
- `locator: Optional[matplotlib.ticker.Locator] = None`  
  明示 Locator。指定時は `ticks` より優先。
- `ticks: Optional[tuple[str, Any]] = ("nbins", 5)`  
  `"nbins" | "interval" | "values" | "auto"` を指定。
  - `("nbins", n)` → `MaxNLocator(nbins=n)`
  - `("interval", step)` → `MultipleLocator(step)`
  - `("values", list)` → `FixedLocator(list)`
  - `("auto", None)` → `AutoLocator()`
  - `None` → `MaxNLocator(nbins=5)`

**メソッド**
- `get_locator() -> matplotlib.ticker.Locator`  
  `locator` があればそれを返す。なければ `ticks` の指定に従って Locator を構築。  
  未知の `kind` の場合は `MaxNLocator(nbins=5)` を返す。

#### `GridConfig`（dataclass）

**フィールド**
- `enabled: bool = True`
- `color: str = "lightgray"`
- `linestyle: str = "--"`
- `linewidth: float = 0.8`
- `x_locator: Optional[matplotlib.ticker.Locator] = None`
- `y_locator: Optional[matplotlib.ticker.Locator] = None`

**用途**
- `plot_on_module` 内のグリッド描画で利用する。`x_locator`/`y_locator` 未指定なら `AxisConfig.get_locator()` の値を使う。

#### `LegendConfig`（dataclass）

**フィールド**
- `enabled: bool = True`
- `loc: str = "best"`
- `ncol: int = 1`
- `frameon: bool = True`
- `fontsize: Optional[float] = None`
- `kwargs: dict[str, Any] = {}`

**メソッド**
- `to_kwargs() -> dict[str, Any]`  
  `kwargs` をベースにしつつ、`loc/ncol/frameon` を `setdefault` で設定。  
  `fontsize` が指定されている場合のみ `fontsize` を付与。

### `matplot_flex/axes_utils.py`

#### `_ensure_primary_axes(fig) -> (Axes, bool)`

**挙動**
- `fig.get_axes()` が存在すれば先頭を返し、`created=False`。
- 存在しなければ `fig.add_axes([0, 0, 1, 1])` で作成し、`created=True`。
- 新規作成時は `ax.set_facecolor("none")` を適用。

#### `get_primary_axes(fig, hide_axis_on_create=False) -> Axes`

**引数**
- `hide_axis_on_create: bool`  
  `True` の場合、新規作成時のみ `axis off` を適用する。

**挙動**
- `_ensure_primary_axes` を呼び出して主Axesを取得する。
- `hide_axis_on_create=True` かつ新規作成時のみ `ax.set_axis_off()` を実行する。

### `matplot_flex/renderers.py`

#### `Renderer`
- `Callable[[matplotlib.axes.Axes, numpy.ndarray, numpy.ndarray], None]`  
  `plot_on_module` の描画コールバック型。

#### `render_line(ax, x, y, color="tab:blue", linewidth=2, **plot_kwargs) -> None`

**挙動**
- `ax.plot(x, y, ...)` を呼び出す。
- `color` と `linewidth` をデフォルトで付与し、残りは `plot_kwargs`。

#### `render_scatter(ax, x, y, **scatter_kwargs) -> None`

**挙動**
- デフォルト: `color="tab:orange"`, `s=50`, `alpha=0.7`, `edgecolors="black"`
- `scatter_kwargs` で上書き可能。
- `ax.scatter(x, y, ...)` を呼び出す。

#### `render_bar(ax, x, y, **bar_kwargs) -> None`

**挙動**
- `width` が未指定の場合、`x` から幅を推定する。
  - `len(x) > 1`: `x` を昇順に並べ、正の差分の最小値を `step` とする（正の差分が無い場合は `1.0`）。
  - `len(x) <= 1`: `step = 1.0`
  - `width = step * 0.8`
- デフォルト: `color="tab:green"`, `alpha=0.6`, `width=推定値`
- `ax.bar(x, y, ...)` を呼び出す。

#### `SeriesSpec`（dataclass）

**用途**
- 複数系列描画のためのデータ・スタイル・レンダラーを一括管理する。

**クラス定数**
- `DEFAULT_COLORS`: 色の既定リスト
- `DEFAULT_LINESTYLES`: `["-", "--", "-.", ":"]`

**フィールド**
- `x: numpy.ndarray`
- `y: numpy.ndarray`
- `renderer: Renderer = render_line`
- `label: Optional[str] = None`
- `color: Optional[str] = None`
- `linestyle: Optional[str] = None`
- `marker: Optional[str] = None`
- `linewidth: Optional[float] = None`
- `kwargs: dict[str, Any] = {}`

**メソッド**
- `__post_init__()`  
  `len(x) != len(y)` の場合は `ValueError`。
- `to_kwargs(default_color=None, default_linestyle=None) -> dict[str, Any]`  
  指定済みの属性を優先し、未指定なら `default_color/default_linestyle` を採用。  
  `label` があれば `label` を含める。

#### `_color_cycle(ax) -> Iterator[str]`

**挙動**
- `ax._get_lines.prop_cycler` の色を優先取得（内部API利用）。  
  取得できない場合は `plt.rcParams["axes.prop_cycle"]` を利用。  
  それでも取得できない場合は `SeriesSpec.DEFAULT_COLORS` を使う。

#### `render_multi(ax, series_specs, legend=None, use_color_cycle=True) -> None`

**引数**
- `series_specs: Iterable[SeriesSpec]`
- `legend: Optional[LegendConfig] = None`
- `use_color_cycle: bool = True`

**挙動**
- `series_specs` を順に描画する。
- 色は `use_color_cycle` が True の場合、`_color_cycle(ax)` を優先。  
  取得できない場合や `None` の場合は `SeriesSpec.DEFAULT_COLORS` を用いる。
- 線種は `SeriesSpec.DEFAULT_LINESTYLES` のサイクルを使用。
- `legend` が指定され、かつ `legend.enabled` で、ラベル付き系列がある場合のみ凡例を描画。

### `matplot_flex/text_utils.py`

#### `draw_rounded_frame(fig, bg_color="#eeeeee", edge_color="black") -> None`

**挙動**
- `get_primary_axes(fig, hide_axis_on_create=True)` で主Axesを取得する。
- `FancyBboxPatch` による角丸矩形を描画する。
- `zorder=-1`, `clip_on=False` で背景として配置する。

#### `format_params(params: dict) -> str`

**挙動**
- 先頭に `$\mathbf{Parameters}:$` を付け、以降は `$key = value$` 形式。
- キーの `_` は `\_` にエスケープ。
- `float` 値は小数2桁で整形。

#### `draw_text(...) -> matplotlib.text.Text`

**シグネチャ**
```
draw_text(
    ax, text, *,
    mode="fit",
    x=0.5, y=0.5,
    transform=None,
    fontsize=12.0,
    min_fontsize=4.0,
    max_fontsize=48.0,
    padding=0.8,
    ha="center", va="center",
    rotation=0.0,
    color="black",
    fontweight="normal",
    target_bbox=None,
) -> matplotlib.text.Text
```

**挙動**
- `transform` 未指定時は `ax.transAxes` を使う。
- `mode="fixed"` の場合は指定 `fontsize` のまま描画して返す。
- `mode="fit"` の場合はテキストとターゲットの bbox を取得し、  
  比率 `min(width_ratio, height_ratio) * padding` でフォントサイズを調整。
- `min_fontsize` と `max_fontsize` の範囲にクランプする。
- bbox 幅/高さが 0 の場合は調整せず返す。

#### `sci_formatter(decimals=1) -> Callable[[float], str]`

**挙動**
- `f"{val:.{decimals}e}"` を返すフォーマッタ関数を生成。

#### `date_formatter(fmt="%Y-%m-%d") -> Callable[[float], str]`

**挙動**
- `matplotlib.dates.num2date` を使い、`strftime(fmt)` で文字列化。

### `matplot_flex/layout.py`

#### `IS_VISIBLE_FRAME: bool`

**用途**
- デバッグ用の分割枠の表示フラグ。  
  `True` の場合のみ `draw_debug_frame` を呼ぶ。

#### `GraphModule`（dataclass, frozen）

**フィールド**
- `x_axis`: 横軸目盛領域の SubFigure
- `x_label`: 横軸ラベル領域の SubFigure
- `y_label`: 縦軸ラベル領域の SubFigure
- `y_axis`: 縦軸目盛領域の SubFigure
- `main`: メイン描画領域の SubFigure
- `title`: タイトル領域の SubFigure

#### `draw_debug_frame(figs) -> None`

**引数**
- `figs`: `Figure` または `SubFigure` の iterable

**挙動**
- `get_primary_axes` で主Axesを取得し、目盛を消した上で枠線を可視化する。
- `IS_VISIBLE_FRAME` が True の場合のみ分割関数から呼ばれる。

#### `get_pixel_size(fig) -> tuple[int, int]`

**挙動**
- `fig.canvas.draw()` を実行し、`fig.bbox` から `width`/`height` を取得。
- 返値はピクセル相当（float だが実装上は `tuple[int, int]` として扱う）。

#### `create_fig(width=1280, height=720) -> matplotlib.figure.Figure`

**挙動**
- `width` と `height` をピクセルとして受け取り、`dpi=100` で `figsize` に変換。  
  `figsize=(width/100, height/100)`。

#### `divide_fig_ratio(fig, direction, ratios) -> list[SubFigure]`

**引数**
- `direction`: `"horizontal"` or `"vertical"`
- `ratios: list[float]`

**挙動**
- `fig.subfigures` を使い比率分割する。  
  `wspace=0`, `hspace=0` を固定。
- `IS_VISIBLE_FRAME` が True の場合のみ `draw_debug_frame` を呼ぶ。

#### `divide_fig_pixel(fig, direction, sizes) -> list[SubFigure]`

**引数**
- `sizes: list[Optional[float]]`  
  `None` が含まれる場合、残余サイズを均等割り当てする。

**挙動**
- 親 Figure のピクセルサイズから `sizes` を比率に換算。
- 指定合計が親サイズを超える場合は `ValueError`。
- `IS_VISIBLE_FRAME` が True の場合のみ `draw_debug_frame` を呼ぶ。

#### `get_padding_subfig(fig, padding=0.1) -> SubFigure`

**挙動**
- 3x3 の GridSpec を作り、中央セルに SubFigure を作成する。
- `padding` は割合指定。上下左右に padding を確保する。
- `constrained_layout` 下でも padding を維持できる設計。
- `IS_VISIBLE_FRAME` が True の場合のみ `draw_debug_frame` を呼ぶ。

#### `draw_graph_module(fig, title_ratio=0.2, label_ratio=0.1, axis_ratio=0.05) -> GraphModule`

**挙動**
- `fig` をサブ図に分割し、タイトル/ラベル/軸/メイン領域を作る。
- 戻り値は `GraphModule`。各領域はフィールドで参照する。
  - `x_axis`, `x_label`, `y_label`, `y_axis`, `main`, `title`

### `matplot_flex/decorators.py`

#### `apply_axis_limits(ax_main, x_cfg, y_cfg, x_min, x_max, y_min, y_max) -> None`
- 主軸の範囲とスケールを設定し、`axis on` を明示する。

#### `draw_grid(ax_main, x_min, x_max, y_min, y_max, grid_cfg, x_locator, y_locator) -> None`
- `GridConfig.enabled` が True の場合、`axvline/axhline` でグリッド線を描画。
- `GridConfig.x_locator`/`y_locator` が未指定なら軸側の locator を使う。

#### `draw_axis_tick_labels(ax_h_axis, ax_v_axis, x_cfg, y_cfg, x_min, x_max, y_min, y_max, x_locator, y_locator) -> None`
- 目盛ラベルを専用の軸領域に `draw_text(mode="fixed")` で配置する。
- ラベル文字列は `AxisConfig.formatter` があればそれを使用する。

#### `draw_axis_labels(ax_h_label, ax_v_label, x_cfg, y_cfg) -> None`
- 軸ラベルを `draw_text(mode="fit")` で描画する。

#### `draw_title(ax_title, title) -> None`
- タイトルを `draw_text(mode="fit")` で描画する。

#### `hide_main_ticks(ax_main) -> None`
- 主軸の `xticks/yticks` を非表示にする。

#### `style_main_spines(ax_main, color="black", linewidth=1.0) -> None`
- 主軸のスパインを表示し、色と太さを揃える。

### `matplot_flex/templates.py`

#### `plot_template(title="Modular Subplot Example", *, width=1200, height=800, ratios=None) -> (fig, figs)`

**挙動**
- `create_fig` で Figure を作成し、`divide_fig_ratio` で縦方向 3 分割する。
- `ratios=None` の場合は `[1, 5, 2]` を使用する。
- `get_primary_axes(figs[0], hide_axis_on_create=True)` にタイトルを `draw_text(mode="fit")` で描画する。
- 戻り値は `(fig, figs)`（`figs` は 3 要素の SubFigure リスト）。

#### `plot_on_module(...) -> None`

**シグネチャ**
```
plot_on_module(
    module,
    x_data,
    y_data,
    title,
    *,
    renderer=render_line,
    x_axis,
    y_axis,
    grid=None,
    series_specs=None,
) -> None
```

**引数**
- `module: GraphModule`  
  `draw_graph_module` が返すモジュール構造。
- `x_data`, `y_data`: `numpy.ndarray`
- `title: str`
- `renderer: Renderer`
- `x_axis: AxisConfig`, `y_axis: AxisConfig`
- `grid: Optional[GridConfig]`
- `series_specs: Optional[Iterable[SeriesSpec]]`

**挙動**
- `module` から `get_primary_axes` で Axes を取得し、役割別に配置する。
- 軸の最小最大値は `series_specs` があれば全系列を結合して算出。  
  それ以外は `x_data`/`y_data` から算出。
- `AxisConfig.range` が指定されている場合はそちらを優先。
- `AxisConfig.get_locator()` で目盛を算出。
- `GridConfig.enabled` が True の場合、`axvline/axhline` でグリッド線を描画。
- `renderer(ax_main, x_data, y_data)` を呼び出してデータ描画。
- 主軸 (`ax_main`) は `axis on` を明示し、`xticks/yticks` は非表示。
- 目盛ラベルは専用の軸領域に `draw_text(mode="fixed")` で配置。
- ラベル文字列は `AxisConfig.formatter` があればそれを使用。

**副作用**
- 渡した `Figure/SubFigure` に対して Axes を追加・設定する。

## 付随スクリプト

### `main.py`

**関数**
- `main(output_path: str | Path = "modular_subplot_example.png") -> None`  
  - `plot_template` で図全体を作成し、左右2分割のサンプルを描く。
  - 左: `render_multi` による sin/cos の重ね描き。
  - 右: `render_scatter` による散布図。
  - 下部に数式とパラメータ表示を配置。
  - `fig.savefig(output_path, dpi=220)` で PNG 出力。

**副作用**
- 指定パスに PNG を生成する。
- 標準出力に `Plotting completed.` を出力。

### `smoke_test.py`

**関数**
- `run() -> None`  
  - `matplotlib.use("Agg")` でヘッドレス実行。
  - `main(output_path=...)` を実行し、PNG が生成されることを `assert` で確認。

**実行方法**
```
python smoke_test.py
```

## 既知の注意点

- `plot_on_module` は `GraphModule` を前提にする。  
  `draw_graph_module` 以外で作成した場合はフィールドの意味が一致している必要がある。
- `render_bar` の幅推定は `x` が非等間隔の場合でも最小正間隔を採用するため、意図せず細い棒になる可能性がある。
- `draw_text(mode="fit")` は `fig.canvas.draw()` を行うため、大量に呼ぶと時間がかかる。
