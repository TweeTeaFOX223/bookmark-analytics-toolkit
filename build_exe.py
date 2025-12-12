"""
PyInstallerを使用してStreamlitアプリをWindows用exeファイルにビルドするスクリプト

使用方法:
    python build_exe.py

ビルド後のファイルは dist/BookmarkAnalyticsToolkit/ に生成されます
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# GitHub Actions等のCI環境でUTF-8出力を強制
if sys.stdout.encoding != "utf-8":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def get_package_data_files():
    """必要なパッケージデータファイルのパスを収集"""
    data_files = []

    # Streamlitの静的ファイル
    try:
        import streamlit

        st_path = Path(streamlit.__file__).parent
        data_files.append((str(st_path / "static"), "streamlit/static"))
        data_files.append((str(st_path / "runtime"), "streamlit/runtime"))
    except ImportError:
        print("警告: Streamlitが見つかりません")

    # SudachiPy辞書
    try:
        import sudachidict_full

        dict_path = Path(sudachidict_full.__file__).parent
        data_files.append((str(dict_path), "sudachidict_full"))
    except ImportError:
        print("警告: sudachidict_fullが見つかりません")

    # matplotlib-fontja (日本語フォント)
    try:
        import matplotlib_fontja

        font_path = Path(matplotlib_fontja.__file__).parent
        data_files.append((str(font_path), "matplotlib_fontja"))
    except ImportError:
        print("警告: matplotlib-fontjaが見つかりません")

    return data_files


def collect_metadata_files():
    """パッケージメタデータを収集"""
    # PyInstallerにパッケージメタデータを含めるための設定
    packages = [
        "streamlit",
        "plotly",
        "altair",
        "pandas",
        "numpy",
        "polars",
        "sudachipy",
        "wordcloud",
        "matplotlib",
        "seaborn",
    ]

    return packages


def create_spec_file():
    """PyInstallerのspecファイルを生成"""
    data_files = get_package_data_files()
    metadata_packages = collect_metadata_files()

    # データファイルのリスト文字列を作成
    datas_str = ",\n    ".join([f"(r'{src}', r'{dst}')" for src, dst in data_files])

    # メタデータパッケージのリスト文字列を作成
    # 各パッケージのメタデータを連結して追加
    copy_metadata_calls = " + ".join([f"copy_metadata('{pkg}')" for pkg in metadata_packages])

    # プロジェクトのsrcディレクトリを追加
    src_dir = str(Path(__file__).parent / "src")

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata, collect_all

block_cipher = None

# メタデータとデータファイルを収集
# collect_allを使ってstreamlit全体（メタデータ含む）を確実に含める
datas, binaries, hiddenimports = collect_all('streamlit')

# 他のパッケージのメタデータも追加
try:
    datas += copy_metadata('plotly')
    datas += copy_metadata('altair')
    datas += copy_metadata('pandas')
    datas += copy_metadata('numpy')
    datas += copy_metadata('polars')
    datas += copy_metadata('sudachipy')
    datas += copy_metadata('wordcloud')
    datas += copy_metadata('matplotlib')
    datas += copy_metadata('seaborn')
except Exception as e:
    print(f"Warning: Some metadata could not be collected: {{e}}")

# 分析対象のメインスクリプト（ラッパーを使用）
a = Analysis(
    [r'build_wrapper.py'],
    pathex=[r'{src_dir}'],
    binaries=binaries,
    datas=datas + [
        {datas_str},
        (r'data', r'data'),  # サンプルデータ
        (r'app.py', r'.'),  # メインアプリケーションファイル
        (r'src', r'src'),  # srcディレクトリ全体（src.パッケージのインポートに必要）
    ],
    hiddenimports=hiddenimports + [
        'streamlit.runtime',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.web',
        'streamlit.web.cli',
        'polars',
        'plotly',
        'matplotlib',
        'seaborn',
        'sudachipy',
        'sudachidict_full',
        'wordcloud',
        'PIL',
        'matplotlib_fontja',
        'bookmark_analytics_toolkit',
        'bookmark_analytics_toolkit.data',
        'bookmark_analytics_toolkit.analysis',
        'bookmark_analytics_toolkit.visualization',
        'bookmark_analytics_toolkit.i18n',
        'importlib.metadata',
        'importlib_metadata',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BookmarkAnalyticsToolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # コンソールを表示（Streamlitの起動ログを確認するため）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがある場合はここに指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BookmarkAnalyticsToolkit',
)
"""

    spec_path = Path(__file__).parent / "BookmarkAnalyticsToolkit.spec"
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    return spec_path


def generate_requirements_from_pyproject():
    """pyproject.tomlからrequirements.txtを生成"""
    print("pyproject.tomlから依存関係を抽出しています...")

    project_root = Path(__file__).parent
    requirements_path = project_root / "requirements.txt"

    try:
        # uv exportを使用してrequirements.txt形式で出力
        result = subprocess.run(
            [
                "uv",
                "export",
                "--format",
                "requirements-txt",
                "--no-hashes",
                "--output-file",
                str(requirements_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"  生成完了: {requirements_path}")

        # PyInstallerを追加（開発依存関係に含まれていない場合）
        with open(requirements_path, "a", encoding="utf-8") as f:
            f.write("\n# Build tool\n")
            f.write("pyinstaller>=6.0.0\n")

        return requirements_path

    except subprocess.CalledProcessError as e:
        print(f"警告: uv exportが失敗しました: {e}")
        print("代替方法として、pyproject.tomlから直接依存関係を読み取ります...")

        # 代替方法: pyproject.tomlを直接パース
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            try:
                import tomli as tomllib
            except ImportError:
                subprocess.run([sys.executable, "-m", "pip", "install", "tomli"], check=True)
                import tomli as tomllib

        pyproject_path = project_root / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        dependencies = pyproject_data.get("project", {}).get("dependencies", [])

        # requirements.txtを生成
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write("# Auto-generated from pyproject.toml\n\n")
            for dep in dependencies:
                f.write(f"{dep}\n")
            f.write("\n# Build tool\n")
            f.write("pyinstaller>=6.0.0\n")

        print(f"  生成完了: {requirements_path}")
        return requirements_path


def check_dependencies():
    """必要な依存関係が揃っているか確認"""
    print("依存関係を確認しています...")

    # PyInstallerの確認（uvで事前にインストールされている必要がある）
    try:
        import PyInstaller

        print(f"  PyInstaller {PyInstaller.__version__} が見つかりました")
    except ImportError:
        print("\nエラー: PyInstallerがインストールされていません")
        print("以下のコマンドでインストールしてください:")
        print("  uv add --dev pyinstaller")
        sys.exit(1)

    # Python 3.10以下の場合、tomliの確認
    if sys.version_info < (3, 11):
        try:
            import tomli

            print(f"  tomli が見つかりました")
        except ImportError:
            print("\nエラー: tomliがインストールされていません（Python 3.10以下で必要）")
            print("以下のコマンドでインストールしてください:")
            print("  uv add --dev tomli")
            sys.exit(1)


def create_readme_txt():
    """配布用のREADME.txtを作成"""
    readme_content = """
================================================================================
Bookmark Analytics Toolkit (BAT) - Windows版
================================================================================

【概要】
ブラウザのブックマークデータを分析・可視化するアプリケーションです。

【使用方法】
1. BookmarkAnalyticsToolkit.exe をダブルクリックして起動
2. コンソールウィンドウが開き、起動処理が開始されます
3. 自動的にブラウザが開き、アプリケーションが表示されます
4. サイドバーからブックマークファイル（CSV/JSON）をアップロード
5. 各タブで様々な分析結果を確認できます

【動作環境】
- Windows 10 / 11 (64bit)
- メモリ: 4GB以上推奨
- ディスク空き容量: 1GB以上

【初回起動について】
- 初回起動時は10〜30秒程度かかる場合があります
- コンソールウィンドウに起動ログが表示されます

【終了方法】
- コンソールウィンドウを閉じる、または
- ブラウザのタブを閉じてからコンソールウィンドウで Ctrl+C

【トラブルシューティング】

Q: アプリが起動しない
A: コンソールウィンドウのエラーメッセージを確認してください
   ポート8501が使用中の場合、他のアプリを終了してから再起動してください

Q: Windows Defenderが警告を出す
A: PyInstallerでパッケージ化されたアプリによくある現象です
   「詳細情報」→「実行」で起動できます
   安全性が心配な場合は、GitHubからソースコードを確認できます

Q: ブラウザが自動で開かない
A: 手動で http://localhost:8501 にアクセスしてください

【ブックマークデータの準備】
1. NirSoftの「WebBrowserBookmarks」をダウンロード
   https://www.nirsoft.net/utils/web_browser_bookmarks_view.html
2. WebBrowserBookmarksを起動（PCのブックマークが自動読込される）
3. Ctrl+Aで全選択→保存ボタンでCSV/JSON形式で保存
4. 保存したファイルを本アプリにアップロード

【機能一覧】
- ブラウザ別分布
- フォルダ別分布
- ドメイン別分布
- 月次・年次トレンド
- 曜日・時間帯パターン
- ヒートマップ
- 階層ツリーマップ
- フォルダツリー
- ワードクラウド
- 単語ランキング

【ライセンス】
MIT License

【お問い合わせ】
GitHub: https://github.com/TweeTeaFOX223/bookmark-analytics-toolkit

================================================================================
"""
    return readme_content.strip()


def create_distribution_package(dist_dir: Path, project_root: Path):
    """配布用パッケージを作成してzip化"""
    print("配布用パッケージを準備しています...")

    # 配布用ディレクトリを作成
    release_dir = project_root / "release"
    release_dir.mkdir(exist_ok=True)

    # 配布用README.txtを作成
    readme_txt_path = dist_dir / "BookmarkAnalyticsToolkit" / "README.txt"
    with open(readme_txt_path, "w", encoding="utf-8") as f:
        f.write(create_readme_txt())
    print(f"  配布用README.txt作成: {readme_txt_path}")

    # zipファイル名を生成（バージョン情報と日付を含む）
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"BookmarkAnalyticsToolkit_Windows_v0.1.0_{timestamp}"
    zip_base_path = release_dir / zip_name

    # zipファイルを作成
    # shutil.make_archiveは拡張子なしのパスを受け取り、.zipを付けたパスを返す
    print(f"  zipファイルを作成中: {zip_base_path}.zip")

    # shutil.make_archiveの戻り値は生成されたアーカイブのフルパス（拡張子付き）
    created_archive = shutil.make_archive(
        str(zip_base_path),  # 拡張子なし
        "zip",
        dist_dir,
        "BookmarkAnalyticsToolkit",
    )

    # 戻り値をPathオブジェクトに変換
    final_zip = Path(created_archive)

    if not final_zip.exists():
        print(f"エラー: zipファイルが生成されませんでした")
        print(f"  期待されたパス: {final_zip}")
        print(f"  make_archiveの戻り値: {created_archive}")
        sys.exit(1)

    zip_size_mb = final_zip.stat().st_size / (1024 * 1024)

    print(f"  完了: {final_zip} ({zip_size_mb:.1f} MB)")
    return final_zip


def build():
    """exeファイルをビルド"""
    print("=" * 60)
    print("Bookmark Analytics Toolkit - Windows exeビルドスクリプト")
    print("=" * 60)
    print()

    # 作業ディレクトリを確認
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"プロジェクトルート: {project_root}")
    print()

    # 依存関係の確認
    check_dependencies()
    print()

    # pyproject.tomlからrequirements.txtを生成
    requirements_path = generate_requirements_from_pyproject()
    print()

    # specファイルを生成
    print("PyInstaller specファイルを生成しています...")
    spec_path = create_spec_file()
    print(f"生成完了: {spec_path}")
    print()

    # 既存のビルド成果物をクリーンアップ
    print("既存のビルド成果物をクリーンアップしています...")
    for dir_name in ["build", "dist"]:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  削除: {dir_path}")
    print()

    # PyInstallerでビルド
    print("PyInstallerでビルドを開始します...")
    print("(このプロセスには数分かかる場合があります)")
    print()

    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", str(spec_path), "--clean"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nエラー: ビルドに失敗しました (終了コード: {e.returncode})")
        sys.exit(1)

    print()
    dist_dir = project_root / "dist"
    exe_path = dist_dir / "BookmarkAnalyticsToolkit" / "BookmarkAnalyticsToolkit.exe"

    if not exe_path.exists():
        print("エラー: 実行ファイルが生成されませんでした")
        sys.exit(1)

    # 配布用パッケージを作成
    print()
    zip_path = create_distribution_package(dist_dir, project_root)

    # 生成されたrequirements.txtをクリーンアップ（オプション）
    if requirements_path.exists():
        print()
        print("一時ファイルをクリーンアップしています...")
        requirements_path.unlink()
        print(f"  削除: {requirements_path}")

    print()
    print("=" * 60)
    print("ビルド完了!")
    print("=" * 60)
    print()
    print(f"【生成ファイル】")
    print(f"  実行ファイル: {exe_path}")
    print(f"  配布用zip : {zip_path}")
    print()
    print("【配布方法】")
    print(f"  {zip_path.name} を配布してください")
    print()
    print("【テスト方法】")
    print(f"  1. {exe_path} をダブルクリック")
    print("  2. ブラウザが自動的に開きます")
    print("  3. サイドバーからブックマークファイルをアップロード")
    print()
    print("【注意事項】")
    print("  - 初回起動時は10〜30秒程度かかります")
    print("  - Windows Defenderが警告を出す場合があります")
    print("    (PyInstallerでパッケージ化されたアプリの一般的な現象)")
    print()


if __name__ == "__main__":
    build()
