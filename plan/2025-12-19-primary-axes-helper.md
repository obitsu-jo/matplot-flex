# 計画書: primary axes ヘルパ導入

## 目的 / スコープ

- 目的: SubFigure/ Figure に対して「1つの主 Axes」を保証する共通ヘルパを追加し、描画の一貫性を高める。
- スコープ: `matplot_flex/axes_utils.py` を追加し、`layout.py` と `text_utils.py` を中心に、該当ドキュメントの更新を行う。
- 非スコープ: 既存APIの互換性を壊す変更（引数型の全面変更など）は行わない。

## 具体手順（順序つき）

1. `matplot_flex/axes_utils.py` を追加し、`get_primary_axes(fig, hide_axis_on_create=False)` を定義する。
2. 内部ヘルパとして `ensure_primary_axes(fig) -> (ax, created)` を用意し、`get_primary_axes` はその Axes のみを返す。
3. `create_frame` を廃止し、デバッグ用の `draw_debug_frame(figs)` を追加する（`IS_VISIBLE_FRAME` が True の場合のみ分割関数内で呼ぶ）。
4. `draw_rounded_frame` を `get_primary_axes` ベースに変更し、`hide_axis_on_create=True` で呼び出す。
5. `plot_template` と `plot_on_module` の `get_axes()[0]` 参照を `get_primary_axes` に置き換える。
6. `plot_on_module` では主軸に対して `axis on` を明示して描画軸を有効化する。
7. `docs/full_reference.md` と `matplot_flex/README.md` にヘルパの仕様と背景描画のルールを追記する。
8. 代表的テストを実行して挙動を確認する（`python -m pytest -q`）。

## 影響範囲・リスク

- 既存の `get_axes()[0]` 前提を `get_primary_axes` に集約するため、想定外の Axes 追加があると表示が変わる可能性がある。
- `create_frame` を廃止するため、枠や目盛を消す処理を呼び出し側で明示する必要がある。
- `draw_rounded_frame` が既存 Axes に描画する場合、軸表示を変更しない前提に依存する。

## 検証観点

- `python -m pytest -q` が通ること。
- `python smoke_test.py` で PNG が生成できること。
- 代表的な `plot_template` + `plot_on_module` の描画が崩れていないこと。

## 実施結果

- `matplot_flex/axes_utils.py` を追加し、`get_primary_axes` を公開。
- `create_frame` を廃止し、`draw_debug_frame` を追加。
- `plot_template` / `plot_on_module` / `draw_rounded_frame` を `get_primary_axes` 経由に統一。
- 関連ドキュメント（`docs/full_reference.md`, `matplot_flex/README.md`, `README.md`）を更新。

## 計画との差分

- `draw_debug_frame` は公開APIに追加せず、`layout.py` 内部用途に限定した。
- テストは未実行（実行はユーザー側で実施予定）。
