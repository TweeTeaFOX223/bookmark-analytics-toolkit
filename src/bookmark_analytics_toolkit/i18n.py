"""多言語対応モジュール - アプリケーションのテキストを日本語と英語で切り替え"""

from typing import Dict, Literal

# 言語タイプの定義
Language = Literal["ja", "en"]


class I18n:
    """多言語対応クラス"""

    # 翻訳辞書
    _translations: Dict[str, Dict[Language, str]] = {
        # アプリケーションタイトル
        "app_title": {"ja": "ブックマーク分析ツールキット", "en": "Bookmark Analytics Toolkit"},
        "app_subtitle": {"ja": "ブックマーク分析", "en": "Bookmark Analyzer"},
        # ボタンとラベル
        "load_file": {"ja": "JSON/CSV読み込み", "en": "Load JSON/CSV"},
        "no_data": {"ja": "データが読み込まれていません", "en": "No data loaded"},
        "analysis_type": {"ja": "分析タイプ:", "en": "Analysis Type:"},
        "appearance": {"ja": "外観:", "en": "Appearance:"},
        "language": {"ja": "言語:", "en": "Language:"},
        # 分析タイプ
        "browser_dist": {"ja": "ブラウザ分布", "en": "Browser Distribution"},
        "folder_dist": {"ja": "フォルダ分布", "en": "Folder Distribution"},
        "domain_dist": {"ja": "ドメイン分布", "en": "Domain Distribution"},
        "monthly_trend": {"ja": "月次推移", "en": "Monthly Trend"},
        "yearly_trend": {"ja": "年次推移", "en": "Yearly Trend"},
        "weekday_pattern": {"ja": "曜日パターン", "en": "Weekday Pattern"},
        "hour_pattern": {"ja": "時間パターン", "en": "Hour Pattern"},
        "weekday_hour_heatmap": {"ja": "曜日-時間ヒートマップ", "en": "Weekday-Hour Heatmap"},
        "hierarchy_treemap": {"ja": "階層ツリーマップ", "en": "Hierarchy Treemap"},
        "folder_tree": {"ja": "フォルダツリー", "en": "Folder Tree"},
        "wordcloud": {"ja": "ワードクラウド", "en": "Word Cloud"},
        "word_ranking": {"ja": "単語ランキング", "en": "Word Ranking"},
        # ウェルカムメッセージ
        "welcome_title": {
            "ja": "ブックマーク分析ツールキットへようこそ",
            "en": "Welcome to Bookmark Analytics Toolkit",
        },
        "welcome_message": {
            "ja": "JSONまたはCSVファイルを読み込んで分析を開始してください",
            "en": "Load a JSON or CSV file to begin analysis",
        },
        # 統計情報
        "loaded": {"ja": "読み込み済み:", "en": "Loaded:"},
        "bookmarks": {"ja": "ブックマーク", "en": "bookmarks"},
        "folders": {"ja": "フォルダ:", "en": "Folders:"},
        "avg_depth": {"ja": "平均深さ:", "en": "Avg Depth:"},
        # グラフタイトル
        "browser_distribution_title": {"ja": "ブラウザ分布", "en": "Browser Distribution"},
        "folder_distribution_title": {
            "ja": "フォルダ分布 (上位{n}件)",
            "en": "Folder Distribution (Top {n})",
        },
        "domain_distribution_title": {
            "ja": "ドメイン分布 (上位{n}件)",
            "en": "Domain Distribution (Top {n})",
        },
        "monthly_trend_title": {
            "ja": "月次ブックマーク作成推移 ({year}年)",
            "en": "Monthly Bookmark Creation ({year})",
        },
        "monthly_trend_title_all": {
            "ja": "月次ブックマーク作成推移 (全期間)",
            "en": "Monthly Bookmark Creation (All Time)",
        },
        "yearly_trend_title": {"ja": "年次ブックマーク作成推移", "en": "Yearly Bookmark Creation"},
        "weekday_pattern_title": {
            "ja": "曜日別ブックマーク作成",
            "en": "Bookmark Creation by Weekday",
        },
        "hour_pattern_title": {
            "ja": "時間別ブックマーク作成",
            "en": "Bookmark Creation by Hour of Day",
        },
        "weekday_hour_heatmap_title": {
            "ja": "ブックマーク作成: 曜日 vs 時間",
            "en": "Bookmark Creation: Weekday vs Hour",
        },
        "hierarchy_treemap_title": {
            "ja": "ブックマーク階層ツリーマップ",
            "en": "Bookmark Hierarchy Treemap",
        },
        "folder_tree_title": {"ja": "フォルダ階層構造", "en": "Folder Hierarchy Structure"},
        "wordcloud_title": {"ja": "ブックマークタイトル ワードクラウド", "en": "Bookmark Title Word Cloud"},
        "word_ranking_title": {
            "ja": "単語出現回数ランキング (上位{n}件)",
            "en": "Word Frequency Ranking (Top {n})",
        },
        # 軸ラベル
        "count": {"ja": "件数", "en": "Count"},
        "percentage": {"ja": "割合 (%)", "en": "Percentage (%)"},
        "browser": {"ja": "ブラウザ", "en": "Browser"},
        "folder": {"ja": "フォルダ", "en": "Folder"},
        "domain": {"ja": "ドメイン", "en": "Domain"},
        "month": {"ja": "月", "en": "Month"},
        "year": {"ja": "年", "en": "Year"},
        "weekday": {"ja": "曜日", "en": "Weekday"},
        "hour": {"ja": "時間", "en": "Hour"},
        "word": {"ja": "単語", "en": "Word"},
        "rank": {"ja": "順位", "en": "Rank"},
        # 曜日名
        "monday": {"ja": "月曜日", "en": "Monday"},
        "tuesday": {"ja": "火曜日", "en": "Tuesday"},
        "wednesday": {"ja": "水曜日", "en": "Wednesday"},
        "thursday": {"ja": "木曜日", "en": "Thursday"},
        "friday": {"ja": "金曜日", "en": "Friday"},
        "saturday": {"ja": "土曜日", "en": "Saturday"},
        "sunday": {"ja": "日曜日", "en": "Sunday"},
        # 月名
        "january": {"ja": "1月", "en": "Jan"},
        "february": {"ja": "2月", "en": "Feb"},
        "march": {"ja": "3月", "en": "Mar"},
        "april": {"ja": "4月", "en": "Apr"},
        "may": {"ja": "5月", "en": "May"},
        "june": {"ja": "6月", "en": "Jun"},
        "july": {"ja": "7月", "en": "Jul"},
        "august": {"ja": "8月", "en": "Aug"},
        "september": {"ja": "9月", "en": "Sep"},
        "october": {"ja": "10月", "en": "Oct"},
        "november": {"ja": "11月", "en": "Nov"},
        "december": {"ja": "12月", "en": "Dec"},
        # メッセージ
        "success": {"ja": "成功", "en": "Success"},
        "error": {"ja": "エラー", "en": "Error"},
        "load_success": {
            "ja": "{count}件のブックマークを読み込みました",
            "en": "Loaded {count} bookmarks successfully!",
        },
        "load_error": {
            "ja": "ファイルの読み込みに失敗しました:\n{error}",
            "en": "Failed to load file:\n{error}",
        },
        "chart_error": {
            "ja": "グラフの生成に失敗しました:\n{error}",
            "en": "Failed to generate chart:\n{error}",
        },
        "no_data_warning": {"ja": "データなし", "en": "No Data"},
        "load_file_first": {
            "ja": "最初にファイルを読み込んでください",
            "en": "Please load a file first",
        },
        # 設定
        "top_n_label": {"ja": "表示件数 (上位n件):", "en": "Top N Items:"},
        "year_filter_label": {"ja": "年フィルタ:", "en": "Year Filter:"},
        "all_years": {"ja": "全期間", "en": "All Years"},
        "height_label": {"ja": "グラフの高さ:", "en": "Chart Height:"},
        "treemap_mode_label": {"ja": "表示モード:", "en": "Display Mode:"},
        "treemap_hierarchical": {"ja": "階層構造", "en": "Hierarchical"},
        "treemap_grouped": {"ja": "グループ別", "en": "Grouped"},
        "colormap_label": {"ja": "カラーマップ:", "en": "Color Map:"},
        "max_words_label": {"ja": "最大単語数:", "en": "Max Words:"},
        "analyzing_text": {"ja": "テキスト解析中...", "en": "Analyzing text..."},
        "no_words_found": {"ja": "単語が見つかりませんでした", "en": "No words found"},
        # ツリー表示
        "url_count": {"ja": "URL数", "en": "URLs"},
        "subfolder_count": {"ja": "子フォルダ数", "en": "Subfolders"},
        "total_items": {"ja": "合計項目数", "en": "Total Items"},
        # 形態素解析設定
        "morphological_analysis_settings": {"ja": "🔧 形態素解析設定", "en": "🔧 Morphological Analysis Settings"},
        "sudachi_mode_about": {"ja": "ℹ️ Sudachiモードについて", "en": "ℹ️ About Sudachi Mode"},
        "sudachi_mode_label": {"ja": "形態素解析モード（Sudachi）", "en": "Morphological Analysis Mode (Sudachi)"},
        "sudachi_mode_a": {"ja": "モードA（短単位）", "en": "Mode A (Short Unit)"},
        "sudachi_mode_b": {"ja": "モードB（中単位）", "en": "Mode B (Medium Unit)"},
        "sudachi_mode_c": {"ja": "モードC（長単位）", "en": "Mode C (Long Unit)"},
        "sudachi_mode_description": {
            "ja": """
**Sudachiの分割モード:**

- **モードA（短単位）**: 最も細かく分割します
  - 例: "東京都" → "東京" + "都"

- **モードB（中単位）**: バランスの取れた分割です
  - 例: "東京都" → "東京都"

- **モードC（長単位）**: 最も長い単位で分割します
  - 例: "東京都庁" → "東京都庁"（複合語を一つの単語として扱う）

💡 モードを変更すると、自動的に再解析されます。
            """,
            "en": """
**Sudachi Splitting Modes:**

- **Mode A (Short Unit)**: Most granular splitting
  - Example: "Tokyo" → "To" + "kyo"

- **Mode B (Medium Unit)**: Balanced splitting
  - Example: "Tokyo" → "Tokyo"

- **Mode C (Long Unit)**: Longest unit splitting
  - Example: "Tokyo Metropolitan Government" → "Tokyo Metropolitan Government" (treats compounds as single words)

💡 Changing the mode will automatically re-analyze the text.
            """,
        },
        "sudachi_mode_changed": {"ja": "✅ モード{mode}に変更しました", "en": "✅ Changed to Mode {mode}"},
        "sudachi_mode_changing": {"ja": "形態素解析モードを変更中...", "en": "Changing morphological analysis mode..."},
    }

    def __init__(self, language: Language = "ja"):
        """
        初期化

        Args:
            language: 表示言語 ('ja' または 'en')
        """
        self._current_language: Language = language

    def get(self, key: str, **kwargs: object) -> str:
        """
        翻訳されたテキストを取得

        Args:
            key: 翻訳キー
            **kwargs: フォーマット用のキーワード引数

        Returns:
            翻訳されたテキスト
        """
        translation: Dict[Language, str] = self._translations.get(key, {})
        text: str = translation.get(self._current_language, key)

        # フォーマット引数があれば適用
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text

        return text

    def set_language(self, language: Language) -> None:
        """
        表示言語を設定

        Args:
            language: 設定する言語 ('ja' または 'en')
        """
        self._current_language = language

    def get_language(self) -> Language:
        """
        現在の言語設定を取得

        Returns:
            現在の言語
        """
        return self._current_language

    def get_weekday_names(self) -> list[str]:
        """
        曜日名のリストを取得

        Returns:
            曜日名のリスト (月曜〜日曜)
        """
        keys: list[str] = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        return [self.get(key) for key in keys]

    def get_month_names(self) -> list[str]:
        """
        月名のリストを取得

        Returns:
            月名のリスト (1月〜12月)
        """
        keys: list[str] = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        return [self.get(key) for key in keys]


# グローバルインスタンス
_i18n_instance: I18n = I18n()


def get_i18n() -> I18n:
    """
    I18nのグローバルインスタンスを取得

    Returns:
        I18nインスタンス
    """
    return _i18n_instance
