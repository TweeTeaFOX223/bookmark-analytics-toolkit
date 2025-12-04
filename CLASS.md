# Bookmark Analytics Toolkit - クラス・機能ドキュメント

このドキュメントは、`src/bookmark_analytics_toolkit`ディレクトリ内のすべてのモジュール、クラス、および主要な機能について説明します。

## 目次

1. [パッケージ情報](#パッケージ情報)
2. [多言語対応 (i18n.py)](#多言語対応-i18npy)
3. [データモジュール (data/)](#データモジュール-data)
4. [分析モジュール (analysis/)](#分析モジュール-analysis)
5. [可視化モジュール (visualization/)](#可視化モジュール-visualization)

---

## パッケージ情報

### `__init__.py`
- **バージョン**: 0.2.0
- **説明**: ウェブブラウザのブックマークを分析するツール

---

## 多言語対応 (i18n.py)

### クラス: `I18n`
アプリケーションの多言語対応を提供するクラス。日本語と英語の2言語をサポート。

#### 主要メソッド:
- `__init__(language: Language = "ja")`: 初期化。デフォルトは日本語
- `get(key: str, **kwargs) -> str`: 翻訳キーから翻訳済みテキストを取得。フォーマット引数にも対応
- `set_language(language: Language) -> None`: 表示言語を設定
- `get_language() -> Language`: 現在の言語設定を取得
- `get_weekday_names() -> list[str]`: 曜日名のリストを取得
- `get_month_names() -> list[str]`: 月名のリストを取得

#### グローバル関数:
- `get_i18n() -> I18n`: グローバルI18nインスタンスを取得

#### サポートされる翻訳キー:
- アプリケーションタイトル、ボタンラベル
- 分析タイプ（ブラウザ分布、フォルダ分布、ドメイン分布など）
- グラフタイトルと軸ラベル
- 曜日名、月名
- メッセージ（成功、エラー、警告）
- 形態素解析設定

---

## データモジュール (data/)

### `__init__.py`
以下のクラスをエクスポート:
- `BookmarkLoader`
- `BookmarkPreprocessor`

---

### クラス: `BookmarkLoader` (loader.py)
JSONまたはCSVファイルからブックマークデータを読み込むクラス。

#### 主要メソッド:

##### `detect_encoding(file_path: Path) -> str` (静的)
ファイルのエンコーディングを自動検出。BOMチェックと複数エンコーディングの試行を実施。

**サポートされるエンコーディング**:
- UTF-8, UTF-16, UTF-32
- Shift_JIS, CP932, EUC-JP, ISO-2022-JP
- Latin1

##### `load(file_path: str | Path, file_type: Optional[Literal["json", "csv"]] = None) -> pl.DataFrame` (静的)
ブックマークファイルを読み込み、Polars DataFrameとして返す。

**引数**:
- `file_path`: ファイルパス
- `file_type`: ファイルタイプ（省略時は拡張子から推測）

**戻り値**: ブックマークデータを含むPolars DataFrame

##### `validate_schema(df: pl.DataFrame) -> bool` (静的)
必要なカラムが存在するか検証。

**必須カラム**:
- Title, URL, Folder Name, Folder Path, Position
- Created Time, ID, Guid, Web Browser, Bookmarks File

##### `get_preview(df: pl.DataFrame, n: int = 10) -> pl.DataFrame` (静的)
最初のn行のプレビューを取得。

---

### クラス: `BookmarkPreprocessor` (preprocessor.py)
ブックマークデータの前処理と派生カラム生成を行うクラス。

#### 主要メソッド:

##### `preprocess(df: pl.DataFrame) -> pl.DataFrame` (静的)
すべての前処理を実行。以下の処理を含む:
- 日時カラムのパース
- 階層カラムの追加
- 時系列カラムの追加
- URLカラムの追加
- メタデータカラムの追加

##### 派生カラム:
- **階層関連**: `folder_path_parts`, `hierarchy_level`, `root_folder`
- **時系列関連**: `created_year`, `created_month`, `created_day`, `created_weekday`, `created_hour`, `created_date`
- **URL関連**: `domain`
- **メタデータ**: `is_modified`, `title_length`

##### フィルタメソッド:
- `filter_by_date_range(df, start_date, end_date)`: 日付範囲でフィルタ
- `filter_by_folder(df, folder_path)`: フォルダパスでフィルタ（部分一致）
- `filter_by_browser(df, browser)`: ブラウザ名でフィルタ
- `search(df, query)`: タイトルまたはURLで検索

---

## 分析モジュール (analysis/)

### `__init__.py`
以下のクラスをエクスポート:
- `HierarchyAnalyzer`
- `StatisticsAnalyzer`
- `TimeSeriesAnalyzer`

---

### クラス: `StatisticsAnalyzer` (statistics.py)
ブックマーク統計を計算する分析クラス。

#### 主要メソッド:

##### `get_basic_stats(df: pl.DataFrame) -> Dict[str, Any]` (静的)
基本統計情報を取得。

**返される情報**:
- `total_bookmarks`: 総ブックマーク数
- `total_folders`: ユニークフォルダ数
- `date_range_start`, `date_range_end`: 日付範囲
- `browsers`: ブラウザ別カウント
- `avg_hierarchy_depth`: 平均階層深さ
- `max_hierarchy_depth`, `min_hierarchy_depth`: 最大・最小階層深さ
- `total_modified`: 変更済みブックマーク数

##### 分布取得メソッド:
- `get_browser_distribution(df) -> pl.DataFrame`: ブラウザ別分布
- `get_folder_distribution(df, top_n=20) -> pl.DataFrame`: 上位N個のフォルダ分布
- `get_domain_distribution(df, top_n=20) -> pl.DataFrame`: 上位N個のドメイン分布
- `get_hierarchy_depth_distribution(df) -> pl.DataFrame`: 階層深さ分布
- `get_root_folder_distribution(df) -> pl.DataFrame`: ルートフォルダ分布

##### `get_title_length_stats(df) -> Dict[str, float]` (静的)
タイトル長の統計（平均、中央値、最大、最小）を取得。

---

### クラス: `TimeSeriesAnalyzer` (timeseries.py)
時系列パターン分析クラス。

#### 主要メソッド:

##### 時系列カウント:
- `get_monthly_counts(df, year=None) -> pl.DataFrame`: 月次カウント（特定年または全期間）
- `get_yearly_counts(df) -> pl.DataFrame`: 年次カウント
- `get_daily_counts(df) -> pl.DataFrame`: 日次カウント

##### パターン分布:
- `get_weekday_distribution(df) -> pl.DataFrame`: 曜日別分布（0=月曜, 6=日曜）
- `get_hourly_distribution(df) -> pl.DataFrame`: 時間別分布（0-23時）

##### ヒートマップデータ:
- `get_weekday_hour_heatmap(df) -> Dict[str, Any]`: 曜日×時間のヒートマップデータ（7×24配列）
- `get_year_month_heatmap(df) -> Dict[str, Any]`: 年×月のヒートマップデータ

##### その他:
- `get_cumulative_counts(df) -> pl.DataFrame`: 累積カウント
- `get_modified_bookmarks_timeline(df) -> pl.DataFrame`: 変更タイムライン
- `get_available_years(df) -> List[int]`: データに含まれる年のリスト

---

### クラス: `HierarchyAnalyzer` (hierarchy.py)
ブックマークフォルダ階層構造の分析クラス。

#### 主要メソッド:

##### `build_treemap_data(df, max_depth=None, hierarchical=True) -> Dict[str, Any]` (静的)
Plotlyツリーマップ用のデータ構造を構築。

**引数**:
- `max_depth`: 最大階層深さ
- `hierarchical`: True=階層構造、False=グループ別

**返される辞書**:
- `labels`: ラベルリスト
- `parents`: 親ノードリスト
- `values`: 値リスト
- `text`: テキストラベルリスト

##### `build_sunburst_data(df, max_depth=None) -> Dict[str, Any]` (静的)
Plotlyサンバーストチャート用のデータ構造を構築。

##### `get_folder_statistics(df) -> pl.DataFrame` (静的)
各フォルダの統計情報を取得。

**返されるカラム**:
- `bookmark_count`: ブックマーク数
- `depth`: 階層深さ
- `first_bookmark`: 最初のブックマーク日時
- `last_bookmark`: 最後のブックマーク日時

##### `get_folder_timeline_heatmap(df, top_n=20) -> Dict[str, Any]` (静的)
上位N個のフォルダの作成タイムラインをヒートマップデータとして取得。

##### `get_hierarchy_tree_structure(df) -> Dict[str, Any]` (静的)
ネストされた辞書形式でツリー構造を取得。

**ツリーノード構造**:
- `name`: フォルダ名
- `children`: 子ノードのリスト
- `url_count`: URL数
- `subfolder_count`: 子フォルダ数

##### `format_tree_text(tree, indent=0) -> str` (静的)
ツリー構造をテキスト形式でフォーマット。

---

### クラス: `TextAnalyzer` (text_analysis.py)
SudachiPyを使用した日本語形態素解析クラス。

#### 主要メソッド:

##### `__init__(mode: str = "C")`:
SudachiPyトークナイザーを初期化。

**分割モード**:
- `A`: 短単位（最も細かい分割）
- `B`: 中単位（バランスの取れた分割）
- `C`: 長単位（最も長い分割、デフォルト）

##### `set_mode(mode: str) -> None`:
分割モードを変更。

##### `extract_words(texts: List[str]) -> List[str]`:
テキストリストから有効な単語を抽出。

**フィルタリング条件**:
- 2文字以上
- 品詞: 名詞、動詞、形容詞のみ
- 除外: 非自立、代名詞、数

##### `get_word_frequency(df, title_column="Title") -> Dict[str, int]`:
DataFrameから単語の出現頻度を計算。

##### `get_top_words(word_freq, top_n=50) -> pl.DataFrame` (静的):
上位N件の単語をDataFrameとして取得。

##### `analyze_text(df, title_column="Title", top_n=50) -> Tuple[Dict[str, int], pl.DataFrame]`:
完全なテキスト分析パイプライン。全単語頻度と上位N件を返す。

---

### クラス: `TextAnalyzerSP` (text_analysis_sp.py)
SentencePieceを使用したテキスト分析クラス。

#### 主要メソッド:

##### `__init__(model_path: str = None)`:
SentencePieceプロセッサを初期化。model_pathが未指定の場合は日本語Wikipediaモデルを自動ダウンロード。

##### `extract_words(texts: List[str]) -> List[str]`:
テキストリストから有効な単語を抽出。

**フィルタリング条件**:
- 2文字以上
- 記号のみを除外
- 数字のみを除外

##### その他のメソッド:
- `get_word_frequency(df, title_column="Title") -> Dict[str, int]`
- `get_top_words(word_freq, top_n=50) -> pl.DataFrame` (静的)
- `analyze_text(df, title_column="Title", top_n=50) -> Tuple[Dict[str, int], pl.DataFrame]`

---

## 可視化モジュール (visualization/)

### `__init__.py`
以下のクラスをエクスポート:
- `PlotlyCharts`
- `MatplotlibCharts`
- `SeabornCharts`

---

### クラス: `PlotlyCharts` (plotly_charts.py)
Plotlyベースのインタラクティブチャート生成クラス。

#### 主要メソッド:

##### `create_bar_chart(df, x_col, y_col, title="棒グラフ", orientation="v", show_values=True, show_percentage=False) -> go.Figure` (静的):
棒グラフを作成。縦向き・横向き対応。

##### `create_line_chart(df, x_col, y_col, title="折れ線グラフ", show_markers=True, show_values=False) -> go.Figure` (静的):
折れ線グラフを作成。

##### `create_pie_chart(df, labels_col, values_col, title="円グラフ") -> go.Figure` (静的):
円グラフを作成。

##### `create_heatmap(heatmap_data, title="ヒートマップ", colorscale="YlOrRd") -> go.Figure` (静的):
ヒートマップを作成。

**引数**:
- `heatmap_data`: `x_labels`, `y_labels`, `values`を含む辞書

##### `create_treemap(treemap_data, title="ツリーマップ", height=600) -> go.Figure` (静的):
ツリーマップを作成。

**引数**:
- `treemap_data`: `labels`, `parents`, `values`, `text`を含む辞書

##### `create_sunburst(sunburst_data, title="サンバーストチャート") -> go.Figure` (静的):
サンバーストチャートを作成。

---

### クラス: `MatplotlibCharts` (matplotlib_charts.py)
Matplotlibベースの静的チャート生成クラス。

#### 主要メソッド:

##### `create_line_chart(df, x_col, y_col, title="Time Series", figsize=(10, 6)) -> Figure` (静的):
折れ線グラフを作成。

##### `create_bar_chart(df, x_col, y_col, title="Bar Chart", figsize=(10, 6), horizontal=False) -> Figure` (静的):
棒グラフを作成。横向き・縦向き対応。

##### `create_histogram(df, col, bins=30, title="Distribution", figsize=(10, 6)) -> Figure` (静的):
ヒストグラムを作成。

##### `create_pie_chart(df, labels_col, values_col, title="Distribution", figsize=(8, 8)) -> Figure` (静的):
円グラフを作成。

##### `create_cumulative_chart(df, x_col, y_col, cumulative_col, title="Cumulative Growth", figsize=(12, 6)) -> Figure` (静的):
日次カウントと累積カウントの2段グラフを作成。

---

### クラス: `SeabornCharts` (seaborn_charts.py)
Seabornベースの統計チャート生成クラス。

#### 主要メソッド:

##### `create_heatmap(heatmap_data, title="Heatmap", figsize=(12, 8), cmap="YlOrRd") -> Figure` (静的):
ヒートマップを作成。

##### `create_boxplot(df, col, title="Box Plot", figsize=(8, 6)) -> Figure` (静的):
ボックスプロットを作成。

##### `create_violin_plot(df, col, title="Violin Plot", figsize=(8, 6)) -> Figure` (静的):
バイオリンプロットを作成。

##### `create_count_plot(df, col, title="Count Plot", figsize=(10, 6), top_n=None) -> Figure` (静的):
カテゴリカルデータのカウントプロットを作成。

---

### クラス: `WordCloudGenerator` (wordcloud_viz.py)
ワードクラウド生成クラス。

#### 主要メソッド:

##### `__init__(font_path: Optional[str] = None)`:
初期化。font_pathが未指定の場合は日本語フォントを自動検出。

##### `generate_wordcloud(word_freq, width=800, height=400, background_color="white", colormap="viridis", max_words=100) -> Image.Image`:
単語頻度辞書からワードクラウド画像（PIL Image）を生成。

##### `generate_wordcloud_figure(word_freq, width=800, height=400, background_color="white", colormap="viridis", max_words=100, title="ワードクラウド") -> plt.Figure`:
ワードクラウドをmatplotlib Figureとして生成。

##### `get_available_colormaps() -> Dict[str, str]` (静的):
利用可能なカラーマップの一覧を取得。

**サポートされるカラーマップ**:
- viridis, plasma, inferno, magma, cividis
- twilight, Blues, Reds, Greens, Purples, Oranges
- RdYlBu, Spectral, coolwarm

---

## 利用例

### 基本的なワークフロー

```python
from bookmark_analytics_toolkit.data import BookmarkLoader, BookmarkPreprocessor
from bookmark_analytics_toolkit.analysis import StatisticsAnalyzer, TimeSeriesAnalyzer
from bookmark_analytics_toolkit.visualization import PlotlyCharts

# 1. データ読み込み
df = BookmarkLoader.load("bookmarks.json")

# 2. 前処理
df = BookmarkPreprocessor.preprocess(df)

# 3. 統計分析
stats = StatisticsAnalyzer.get_basic_stats(df)
browser_dist = StatisticsAnalyzer.get_browser_distribution(df)

# 4. 時系列分析
monthly = TimeSeriesAnalyzer.get_monthly_counts(df)
weekday = TimeSeriesAnalyzer.get_weekday_distribution(df)

# 5. 可視化
fig = PlotlyCharts.create_bar_chart(browser_dist, "Web Browser", "count")
fig.show()
```

---

このドキュメントは、プロジェクトのソースコード（バージョン0.2.0）を基に自動生成されました。
