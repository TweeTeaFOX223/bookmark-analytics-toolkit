"""
Streamlitアプリケーション起動用ラッパー

PyInstallerでパッケージ化する際のエントリーポイントとして使用します。
このスクリプトはStreamlitのCLIを適切に起動します。
"""

import sys
import os
from pathlib import Path
import traceback


def main():
    """Streamlitアプリケーションを起動"""
    try:
        # 実行ファイルのディレクトリを取得
        if getattr(sys, "frozen", False):
            # PyInstallerでパッケージ化されている場合
            # sys._MEIPASSは一時的な解凍ディレクトリ（_internalディレクトリ）
            application_path = Path(sys._MEIPASS)
            print(f"[DEBUG] PyInstaller環境で実行中")
            print(f"[DEBUG] sys._MEIPASS: {sys._MEIPASS}")
        else:
            # 通常のPythonスクリプトとして実行されている場合
            application_path = Path(__file__).parent
            print(f"[DEBUG] 通常のPython環境で実行中")

        print(f"[DEBUG] アプリケーションパス: {application_path}")

        # application_pathをsys.pathに追加（src.パッケージのインポートを可能にする）
        if str(application_path) not in sys.path:
            sys.path.insert(0, str(application_path))
            print(f"[DEBUG] sys.pathに追加: {application_path}")

        # app.pyのパスを設定
        app_path = application_path / "app.py"
        print(f"[DEBUG] app.pyのパス: {app_path}")
        print(f"[DEBUG] app.pyの存在確認: {app_path.exists()}")

        if not app_path.exists():
            print("\n" + "=" * 60)
            print("エラー: app.py が見つかりません")
            print("=" * 60)
            print(f"探索パス: {app_path}")
            print(f"アプリケーションパス: {application_path}")
            print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
            if hasattr(sys, "_MEIPASS"):
                print(f"sys._MEIPASS: {sys._MEIPASS}")
                # _MEIPASSディレクトリの内容を表示
                print("\n_MEIPASSディレクトリの内容:")
                try:
                    for item in Path(sys._MEIPASS).iterdir():
                        print(f"  - {item.name}")
                except Exception as e:
                    print(f"  ディレクトリ読み込みエラー: {e}")
            print("\nEnterキーを押して終了...")
            input()
            sys.exit(1)

        # Streamlitを起動
        print("\n" + "=" * 60)
        print("Bookmark Analytics Toolkit")
        print("=" * 60)
        print()
        print("アプリケーションを起動しています...")
        print("ブラウザが自動的に開きます。")
        print("終了するには、このウィンドウを閉じてください。")
        print()

        # StreamlitのCLIを呼び出し
        print("[DEBUG] Streamlitをインポート中...")
        from streamlit.web import cli as stcli

        print("[DEBUG] Streamlit CLIを起動中...")
        sys.argv = [
            "streamlit",
            "run",
            str(app_path),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
            "--global.developmentMode=false",
        ]

        print(f"[DEBUG] sys.argv: {sys.argv}")
        sys.exit(stcli.main())

    except Exception as e:
        print("\n" + "=" * 60)
        print("予期しないエラーが発生しました")
        print("=" * 60)
        print(f"\nエラー内容:")
        print(f"{type(e).__name__}: {e}")
        print("\n詳細なトレースバック:")
        traceback.print_exc()
        print("\nEnterキーを押して終了...")
        input()
        sys.exit(1)


if __name__ == "__main__":
    main()
