# Bookmark Analytics Toolkit (BAT)

[NirSoftのWebBrowserBookmarks(フリーソフト)](https://www.nirsoft.net/utils/web_browser_bookmarks_view.html)を使って出力した、お手元のPCに入っているブラウザのブックマークデータ(CSV/JSON)を分析するための PythonのGUIアプリ(Streamlit)です。

ブラウザのブックマーク機能を多用している方が本アプリを使用すると、自分のネット歴を詳細に振り返ることができます。

アプリをインストールした時の容量は約800MBです　→約300MBがSudachiPyの辞書、残りがPython本体とPythonパッケージになります。


## ★機能一覧

### 12の方法でブックマークを分析  
以下のような分析ができます。※知人のブクマで試したのでプライバシー保護のモザイクが付いています。

1. **Browser Distribution** - ブラウザ種別のブックマーク分布（棒グラフ、パーセンテージ付き）
![a1](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/1_BrowserDistribution.png)

<hr/>  
  
2. **Folder Distribution** - フォルダ別のブックマーク分布（上位n件、件数表示）  
![a2](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/2_FolderDistribution.png)

<hr/>  
  
3. **Domain Distribution** - ドメイン別のブックマーク分布（上位n件、件数・パーセンテージ表示）  
![a3](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/3_DomainDistribution.png)

<hr/>  
  
4. **Monthly Trend** - 月次のブックマーク作成推移（折れ線グラフ、年フィルタ付き）  
![a4](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/4_MonthlyTrend.png)  

<hr/>  
  
5. **Yearly Trend** - 年次のブックマーク作成推移（折れ線グラフ）
![a5](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/5_YearlyTrend.png)

<hr/>  
  
6. **Weekday Pattern** - 曜日別のブックマーク作成パターン  
![a6](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/6_WeekdayPattern.png)  

<hr/>  
  
7. **Hour Pattern** - 時間別のブックマーク作成パターン  
![a7](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/7_HourPattern.png)

<hr/>  
  
8. **Weekday-Hour Heatmap** - 曜日と時間のヒートマップ  
![a8](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/8_Weekday-HourHeatmap.png)  

<hr/>  
  
9.  **Hierarchy Treemap** - フォルダ階層のツリーマップ（階層構造/グループ別切り替え可能）  
![a9](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/9_HierarchyTreemap.png)  

<hr/>  
  
10. **Folder Tree** - フォルダ階層のテキストツリー表示  
![a10](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/10_FolderTree.png)  

<hr/>  
  
11. **Word Cloud** - ブックマークタイトルの単語頻度をワードクラウドで可視化（日本語形態素解析対応）  
![a11](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/11_FolderTree.png)  

<hr/>  
  
12. **Word Ranking** - 単語出現回数ランキング（CSV/JSONダウンロード可能）  
![a12](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/12_WordRanking.png)  
### 便利なサイドバー設定
- **グローバル年フィルタ**: サイドバーから特定の年を選択してすべてのグラフをフィルタリング
- **形態素解析モード選択**: Sudachiの分割モード（短単位/中単位/長単位）を切り替え可能
- **多言語対応**: 日本語/英語の切り替え（UIとグラフのすべての要素に対応）
![b2](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/SideBar.png)  


### ブクマ内に変な文字があってもOK
- 複数のエンコーディング対応（UTF-8, UTF-16, Shift-JIS, CP932など）

## ★目次
- [Bookmark Analytics Toolkit (BAT)](#bookmark-analytics-toolkit-bat)
  - [★機能一覧](#機能一覧)
    - [12の方法でブックマークを分析](#12の方法でブックマークを分析)
    - [便利なサイドバー設定](#便利なサイドバー設定)
    - [ブクマ内に変な文字があってもOK](#ブクマ内に変な文字があってもok)
  - [★目次](#目次)
  - [★使用方法](#使用方法)
    - [１：WebBrowserBookmarksをインストール](#１webbrowserbookmarksをインストール)
    - [２：ブックマークデータをCSV/JSONに出力](#２ブックマークデータをcsvjsonに出力)
    - [３：Pythonとuvのインストール](#３pythonとuvのインストール)
    - [４：パッケージDLとアプリ起動](#４パッケージdlとアプリ起動)
    - [５：基本的な操作フロー](#５基本的な操作フロー)
  - [★プロジェクト構造](#プロジェクト構造)
  - [★技術スタック](#技術スタック)
  - [★雑記](#雑記)
    - [srcフォルダの中身](#srcフォルダの中身)
    - [streamlitのUI作成(地獄)](#streamlitのui作成地獄)
  - [ライセンス](#ライセンス)


## ★使用方法


### １：WebBrowserBookmarksをインストール

このアプリはNirSoftのフリーソフト「WebBrowserBookmarks」を使用して、PC内にインストールされている各ブラウザからエクスポートした、ブックマークのファイル(CSV/JSON)を分析するというものです。

最初にNirSoftの公式サイトからWebBrowserBookmarksをDLしてください。
**https://www.nirsoft.net/utils/web_browser_bookmarks_view.html**

※NirSoftはフリーソフト開発で有名な歴史ある団体です。安全性は大丈夫と思います。

老舗のフリーソフト公開サイト“nirsoft.net”が15周年 ～テスト版ツールの公開ページがお披露目  
https://forest.watch.impress.co.jp/docs/news/1203753.html

### ２：ブックマークデータをCSV/JSONに出力

WebBrowserBookmarksを起動すると、自動的にPC内のブラウザのブックマークのデータがあるフォルダが読み込まれます。

Ctrl+Aでブックマークを全選択して左上の保存ボタンを押すことで、ブラウザブックマークをCSV/JSONに変換してエクスポートすることができます。
![b1](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/Export1.png)  
![b2](https://raw.githubusercontent.com/TweeTeaFOX223/bookmark-analytics-toolkit/refs/heads/main/screenshots/Export2.png)  


CSV/JSONには、隠し項目含むブックマークの全データ(タイトル・URL・フォルダ名・フォルダパス・位置・作成日時・変更日時・固有ID等)が含まれるようになっています。通常ではブラウザから見ることが出来ないデータです。下記はJSONの中身です。CSVも同じ感じです。
```json
[
  {
    "Title": "文字列 - ブックマークのタイトル",
    "URL": "文字列 - ブックマークのURL",
    "Folder Name": "文字列 - 所属フォルダ名",
    "Folder Path": "文字列 - フォルダの階層パス(\\区切り)",
    "Position": "文字列(数値) - ブックマークの位置",
    "Created Time": "文字列 - 作成日時(YYYY/MM/DD HH:MM:SS形式)",
    "Modified Time": "文字列 - 更新日時(空文字列の場合あり)",
    "ID": "文字列(数値) - 一意のID",
    "Guid": "文字列 - グローバル一意識別子",
    "Web Browser": "文字列 - ブラウザ名(Chrome/Firefox等)",
    "Bookmarks File": "文字列 - ブックマークファイルのパス"
  }
]
```


### ３：Pythonとuvのインストール
このアプリはパッケージとPython仮想環境の管理に **uv** を使用しています。uvをインストールしないと起動することができません。

まだuvをインストールしていない場合：

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### ４：パッケージDLとアプリ起動

```bash
# リポジトリをクローン
git clone <repository-url>
cd bookmark-analytics-toolkit

# 依存パッケージのインストール（uvが自動的に仮想環境を作成・管理）
uv sync

# Streamlitアプリケーションの実行
uv run streamlit run app.py
```

アプリケーションが起動すると、ブラウザで `http://localhost:8501` が自動的に開きます。


### ５：基本的な操作フロー
起動に成功したならば、後は画面通りにやれば使用できると思います。


1. アプリケーションを起動: `uv run streamlit run app.py`
2. サイドバーの「ファイルアップロード」からJSONまたはCSVファイルを選択
3. データが読み込まれると、各タブでリアルタイムに分析結果が表示されます
4. 各タブの設定パネルで表示内容をカスタマイズできます
5. 実際に触って色々と遊んでみてください。


## ★プロジェクト構造

```
bookmark-analytics-toolkit/
├── pyproject.toml                  # プロジェクト設定ファイル（hatchling使用）
├── LICENSE                         # ライセンスファイル
├── README.md                       # プロジェクト説明
├── app.py                          # Streamlitアプリケーション（エントリーポイント）
├── data/                           # サンプルデータ
│   └── sample.json
└── src/
    └── bookmark_analytics_toolkit/
        ├── __init__.py             # パッケージ情報（バージョン: 0.2.0）
        ├── i18n.py                 # 多言語対応モジュール（日本語・英語）
        ├── data/                   # データローディングと前処理
        │   ├── __init__.py
        │   ├── loader.py           # JSON/CSVファイルの読み込み
        │   └── preprocessor.py     # データ前処理と派生カラム生成
        ├── analysis/               # データ分析モジュール
        │   ├── __init__.py
        │   ├── statistics.py       # 統計分析（分布、基本統計）
        │   ├── timeseries.py       # 時系列分析（月次/年次/曜日/時間パターン）
        │   ├── hierarchy.py        # 階層構造分析（ツリーマップ、フォルダ統計）
        │   ├── text_analysis.py    # テキスト分析（SudachiPy形態素解析）
        │   └── text_analysis_sp.py # テキスト分析（SentencePiece版）
        └── visualization/          # グラフ描画モジュール
            ├── __init__.py
            ├── plotly_charts.py    # Plotlyインタラクティブチャート
            ├── matplotlib_charts.py # Matplotlib静的チャート
            ├── seaborn_charts.py   # Seaborn統計チャート
            └── wordcloud_viz.py    # ワードクラウド生成
```

## ★技術スタック

「uvとStreamlitとPolarsとSudachiPyの使用」「12個の分析方法」を指定の上、後はClaudeに選定させました。

ブクマのような文字中心データの分析や可視化となると、まあこの辺だろなという気がします。

| 技術項目                       | 使用しているもの                    |
| ------------------------------ | ----------------------------------- |
| AI エージェント                | Claude Code（Sonnet 4.5）           |
| プログラミング言語             | Python 3.12+                        |
| 仮想環境・パッケージ管理                 | uv                         |
| リンター（開発用）             | Ruff 0.1.0+                         |
| データ処理フレームワーク       | Polars 0.20.0+                      |
| WebUIフレームワーク            | Streamlit 1.51.0+                   |
| インタラクティブ可視化         | Plotly 5.18.0+                      |
| 静的グラフ可視化               | Matplotlib 3.8.0+ / Seaborn 0.13.0+ |
| 日本語フォント対応             | matplotlib-fontja 1.1.0+            |
| 日本語形態素解析               | SudachiPy 0.6.0+ (辞書: full版)     |
| ワードクラウド生成             | WordCloud 1.9.0+                    |


## ★雑記

### srcフォルダの中身
CLASS.mdにClaude Codeに分析させて書かせた説明を置いてあります。同じような文章データを解析してみたいって人はsrcの中身をぜひ流用してください。


**srcフォルダのリンク**  
https://github.com/TweeTeaFOX223/bookmark-analytics-toolkit/tree/main/src/bookmark_analytics_toolkit  
**srcフォルダの中身の分析解説ページ(Claudeによるもの)**
https://github.com/TweeTeaFOX223/bookmark-analytics-toolkit/blob/main/CLASS.md  

### streamlitのUI作成(地獄)
今回はほぼClaude Code中心のVibe Codingで作ったのですが、それでも`app.py`のUI調節が地獄でした。Reactと比較してレンダリング周りが非常に難しかった。

「年フィルタの全期間のチェックを外す →年指定フィルタの一覧を表示＋データ内の最新年(2025年)にチェックを入れる →グラフの再読み込み」という処理の実装をClaudeに50回近く指示したのですが、それが全く上手く行かない。

結局は人力で`st.rerun()`の位置が原因と特定して、それの修正を指示するまで実装ができませんでした…。  

**`app.py`(StreamlitのGUI構成のファイル)**
https://github.com/TweeTeaFOX223/bookmark-analytics-toolkit/blob/main/app.py  


## ライセンス

MIT Licenseです。