# 他者利用に向けた問題点・改善点

この文書は、リポジトリを「他人に使ってもらえるレベル」に引き上げるための論点整理です。

## 問題点

- パッケージメタデータ不足: `LICENSE` が存在しない、`pyproject.toml` の `project.urls` がプレースホルダ（`https://example.com/...`）。（対応済み: `LICENSE` 追加、URL 更新）
- 依存関係の二重管理: `pyproject.toml` は未固定、`requirements.txt` は固定版で乖離の可能性。（対応済み: 範囲指定と固定版の運用方針を明文化）
- リポジトリ衛生: `.gitignore` がなく、`matplot_flex/__pycache__/` と `modular_subplot_example.png` が追跡対象。（対応済み: `.gitignore` 追加、追跡ファイル整理）
- ドキュメント不足: ルートの `README.md` が英語中心で、利用前提/対応範囲/互換性/詳細な使用例が不足。（対応済み: ルート README の日本語化）
- テスト/CI不足: `smoke_test.py` のみで自動実行環境がない。（対応済み: GitHub Actions 追加、pytest 追加）
- ドキュメント記載不足: `matplot_flex/layout.py` の `plot_template` の `ratios` デフォルト値と戻り値が文書で明確でない。（対応済み: 文書を実装に合わせて修正）

## 改善点（優先度順）

### 高

- `LICENSE` を追加し、`pyproject.toml` のメタデータ（URL、作者、ライセンス、Classifier）を整備する。（対応済み）
- `.gitignore` を追加し、生成物（`__pycache__/`, 画像出力, など）を追跡対象から外す。（対応済み）
- 依存関係の運用方針を明確化する（`pyproject.toml` と `requirements.txt` の整合、必要ならロックファイル）。（対応済み）
- ルート `README.md` を日本語（必要なら英語併記）で拡充し、目的・前提・対応環境・導入手順・代表的ユースケースを明記する。（対応済み）
- CI を導入し、`smoke_test.py` や基本的なテストを自動実行する。（対応済み）

### 中

- `plot_template` の `ratios` デフォルト値と戻り値の仕様を文書で明記する。（対応済み）
- バージョニング方針と `CHANGELOG` を用意する。（対応済み）
- 代表的な利用パターンのテスト（複数系列、棒グラフ、日付軸など）を追加する。（対応済み）

### 低

- コーディング規約・静的解析（ruff/mypy 等）の導入検討
- `docs/` 配下に API 仕様・設計メモ・運用ガイドを追加する
