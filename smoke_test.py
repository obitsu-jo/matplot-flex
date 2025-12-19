import pathlib
import matplotlib

# バックエンドを固定してGUI不要で実行できるようにする
matplotlib.use("Agg")

from main import main


def run() -> None:
    """簡易スモークテスト: 描画が通ってPNGが生成されることだけ確認"""
    out_path = pathlib.Path(__file__).parent / "modular_subplot_example.png"
    if out_path.exists():
        out_path.unlink()
    main(output_path=out_path)
    assert out_path.exists(), "Output PNG was not created by main()."
    print("Smoke test passed. PNG generated at", out_path)


if __name__ == "__main__":
    run()
