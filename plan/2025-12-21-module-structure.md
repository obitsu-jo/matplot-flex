# 計画: モジュール構成整理

## 目的 / スコープ
- 目的: `matplot_flex` 内の責務分離を明確化し、描画/装飾/レイアウト/合成の境界を整理する。
- スコープ（In）:
  - `plot_template` / `plot_on_module` の配置見直し
  - `decorators.py` / `templates.py` の新設と最低限の移設
  - ファイル内の関数順の整理（関連性と依存順に合わせる）
  - `__init__.py` と README 群の更新
- スコープ（Out）:
  - 既存APIの破壊的変更
  - 描画仕様の大幅な改変
  - 無関係な整形・リネーム

## 具体手順（順序つき）
1. 既存構成と依存関係を整理する（`matplot_flex/layout.py`、`matplot_flex/renderers.py`、`matplot_flex/text_utils.py`、`matplot_flex/axes_utils.py`、`matplot_flex/__init__.py`、`README.md`、`matplot_flex/README.md`）。
2. `matplot_flex/templates.py` を新規作成し、`plot_template` と `plot_on_module` を移動する。
3. `plot_on_module` 内の装飾処理（グリッド、軸/ラベル/タイトル、tick ラベル描画）を関数化し、`matplot_flex/decorators.py` に移動する。
4. `matplot_flex/layout.py` から `plot_template` / `plot_on_module` の定義を削除し、関連 import を整理する。
5. 各モジュール内の関数順を整理し、関連関数が近接するように配置する。
6. `matplot_flex/__init__.py` の再エクスポートと README 群の構成説明を更新し、公開APIは維持する。
7. サンプルとテストで挙動が変わらないことを確認する。

## 影響範囲・リスク
- `plot_on_module` 分割に伴う描画順序の微妙な変更リスク。
- 新規モジュール追加による import 循環の発生リスク。
- README の構成説明更新漏れによる利用者混乱。

## 検証観点
- `python smoke_test.py` で PNG 生成が成功する。
- `python -m pytest -q` が通る（任意だが可能なら実施）。
- README のクイックスタートが変更不要で動作する。

## 実施結果
- `matplot_flex/decorators.py` と `matplot_flex/templates.py` を新設し、装飾処理と合成処理を分離。
- `matplot_flex/layout.py` から `plot_template` / `plot_on_module` を削除し、レイアウト専用に整理。
- `matplot_flex/__init__.py` の import を更新し、公開APIを維持。
- README 群（`README.md`, `matplot_flex/README.md`, `docs/full_reference.md`）の構成説明を更新。
- 関連モジュール内の関数順を補助関数 → 公開関数の順に整理。

## 計画との差分
- なし（計画通りに実施）。
