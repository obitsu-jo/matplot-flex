# CHANGELOG

このプロジェクトの変更履歴を記録します。

## [Unreleased]

- 未リリースの変更

## [0.2.0] - 2025-12-22

- 破壊的変更: `draw_graph_module` が `GraphModule` を返すように変更し、`plot_on_module` も `GraphModule` 前提に統一
- 破壊的変更: `render_multi` から凡例描画を削除し、`LegendItem` + `draw_legend` の独立描画へ移行
- `LegendConfig` を拡張し、`items/position/offset/target` による凡例配置制御を追加
- `LegendPosition` を Matplotlib の loc 名に合わせて追加
- `AxisConfig.pad` で自動レンジに余白を追加
- `draw_rounded_frame` / `draw_text` に `zorder` を追加、`draw_text_on_fig` を新設
- ドキュメントとサンプルを新仕様に更新

## [0.1.1] - 2025-12-19

- メタデータとライセンスの整備（MIT、authors、URL、Classifiers）
- CI と pytest テストの追加、スモークテストの継続
- README と docs の整備（運用方針、利用手順、変更履歴）
- 依存関係の範囲指定と開発手順の明記

## [0.1.0] - 2025-01-01

- 初期リリース
