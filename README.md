# Matplot Flex
[![CI](https://github.com/obitsu-jo/matplot-flex/actions/workflows/ci.yml/badge.svg)](https://github.com/obitsu-jo/matplot-flex/actions/workflows/ci.yml)

モジュール化されたサブプロット構成、テキストのフィット、基本レンダラーをまとめた Matplotlib 補助ライブラリです。

## 構成
- `matplot_flex/config.py`: 軸/凡例/グリッド設定。
- `matplot_flex/text_utils.py`: テキストフィット、パラメータ整形、角丸フレーム、日付/指数フォーマッタ。
- `matplot_flex/renderers.py`: 折れ線/散布/棒グラフ、複数系列補助、`SeriesSpec`。
- `matplot_flex/layout.py`: Figure/SubFigure 生成と `plot_on_module` の司令塔。
- `main.py`: `modular_subplot_example.png` を生成するサンプル。
- `smoke_test.py`: 生成確認の簡易テスト。

公開APIは `matplot_flex/__init__.py` から再エクスポートしています。  
詳細なAPIノートは `matplot_flex/README.md` を参照してください。

## 対応環境
- Python 3.10 以上

## クイックスタート
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

## サンプルの実行
```
python main.py
```
リポジトリ直下に `modular_subplot_example.png` を出力します。

## CI
GitHub Actions で `python smoke_test.py` を実行します。

## テスト
```
python smoke_test.py
```
PNG を再生成して、生成できたことを確認します。

```
python -m pytest -q
```
代表的な利用パターンの描画が通ることを確認します。

## 依存関係の方針
ライブラリ利用向けの範囲指定は `pyproject.toml` で管理し、開発・CI の再現性は `requirements.txt` の固定版で担保します。

開発環境の導入:
```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## バージョニング方針
SemVer（MAJOR.MINOR.PATCH）に従います。変更履歴は `CHANGELOG.md` を参照してください。

- MAJOR: 互換性のない変更
- MINOR: 後方互換のある機能追加
- PATCH: 後方互換のあるバグ修正

## ローカルパッケージとして導入（再利用向け）
```
pip install -e .
```
以降は同一環境の別ディレクトリから `import matplot_flex` できます。

## ライセンス
MIT License（`LICENSE` を参照）
