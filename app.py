"""Streamlitベースのブックマーク分析アプリケーション"""

from plotly.graph_objs._figure import Figure
import streamlit as st
import polars as pl
import tempfile
from typing import Optional, List, Dict, Any, Sequence
from pathlib import Path

from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.uploaded_file_manager import UploadedFile

from bookmark_analytics_toolkit.i18n import I18n
from src.bookmark_analytics_toolkit.data import BookmarkLoader, BookmarkPreprocessor
from src.bookmark_analytics_toolkit.analysis import (
    StatisticsAnalyzer,
    TimeSeriesAnalyzer,
    HierarchyAnalyzer,
)

# SudachiPy版を使用
from src.bookmark_analytics_toolkit.analysis.text_analysis import TextAnalyzer
from src.bookmark_analytics_toolkit.visualization import PlotlyCharts
from src.bookmark_analytics_toolkit.visualization.wordcloud_viz import WordCloudGenerator
from src.bookmark_analytics_toolkit.i18n import get_i18n

# ページ設定
st.set_page_config(
    page_title="Bookmark Analytics Toolkit",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# タブを改行可能にするカスタムCSS
st.markdown(
    """
<style>
    /* タブコンテナを改行可能にする */
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: 8px;
        row-gap: 8px;
    }

    /* 個別のタブボタン */
    .stTabs [data-baseweb="tab"] {
        flex-shrink: 0;
        white-space: nowrap;
        margin-right: 4px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# セッション状態の初期化
if "df" not in st.session_state:
    st.session_state.df = None
if "preprocessed_df" not in st.session_state:
    st.session_state.preprocessed_df = None
if "language" not in st.session_state:
    st.session_state.language = "ja"
if "word_analysis_cache" not in st.session_state:
    st.session_state.word_analysis_cache = None  # 年毎の単語出現頻度キャッシュ
if "sudachi_mode" not in st.session_state:
    st.session_state.sudachi_mode = "C"  # デフォルトはモードC
if "applied_use_all_years" not in st.session_state:
    st.session_state.applied_use_all_years = True  # 適用済みの全期間フラグ
if "applied_selected_years" not in st.session_state:
    st.session_state.applied_selected_years = []  # 適用済みの選択された年
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None  # アップロードされたファイル名

# 多言語対応
i18n: I18n = get_i18n()
i18n.set_language(st.session_state.language)


def load_data(uploaded_file) -> None:
    """データを読み込む"""
    try:
        # 一時ファイルに保存（Windows/Linux/Mac互換）
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=Path(uploaded_file.name).suffix
        ) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_path = Path(tmp_file.name)

        # データ読み込み
        df: pl.DataFrame = BookmarkLoader.load(temp_path)
        BookmarkLoader.validate_schema(df)

        # 前処理
        preprocessed_df: pl.DataFrame = BookmarkPreprocessor.preprocess(df)

        # テキスト分析のキャッシュを生成（年毎に分析）
        with st.spinner(i18n.get("analyzing_text")):
            text_analyzer = TextAnalyzer(mode=st.session_state.sudachi_mode)
            word_analysis_cache = _build_word_analysis_cache(preprocessed_df, text_analyzer)

        # セッション状態に保存
        st.session_state.df = df
        st.session_state.preprocessed_df = preprocessed_df
        st.session_state.word_analysis_cache = word_analysis_cache
        st.session_state.uploaded_filename = uploaded_file.name  # ファイル名を保存

        # 年フィルタをリセット（全期間に戻す）
        st.session_state.applied_use_all_years = True
        st.session_state.applied_selected_years = []

        st.success(i18n.get("load_success", count=len(df)))

    except Exception as e:
        st.error(i18n.get("load_error", error=str(e)))


def _build_word_analysis_cache(df: pl.DataFrame, text_analyzer: TextAnalyzer) -> Dict[str, Any]:
    """
    年毎に形態素解析を実行し、単語出現頻度をキャッシュ

    Returns:
        {
            'all': {'単語': 出現回数, ...},  # 全期間
            2023: {'単語': 出現回数, ...},    # 2023年
            2024: {'単語': 出現回数, ...},    # 2024年
            ...
        }
    """
    cache: Dict[str, Dict[str, int]] = {}

    # 全期間の分析
    word_freq_all = text_analyzer.get_word_frequency(df, title_column="Title")
    cache["all"] = word_freq_all

    # 年毎の分析
    if "created_year" in df.columns:
        years = df["created_year"].unique().sort().to_list()
        for year in years:
            if year is not None:
                year_df = df.filter(pl.col("created_year") == year)
                word_freq_year = text_analyzer.get_word_frequency(year_df, title_column="Title")
                cache[int(year)] = word_freq_year

    return cache


def _get_word_freq_from_cache(
    cache: Dict[str, Dict[str, int]], use_all_years: bool, selected_years: List[int]
) -> Dict[str, int]:
    """
    キャッシュから該当する年の単語頻度を取得

    Args:
        cache: 単語頻度キャッシュ
        use_all_years: 全期間を使用するか
        selected_years: 選択された年のリスト

    Returns:
        単語頻度の辞書
    """
    if use_all_years:
        # 全期間
        return cache.get("all", {})
    elif not selected_years:
        # 年が選択されていない場合は空
        return {}
    elif len(selected_years) == 1:
        # 単一年の場合
        return cache.get(selected_years[0], {})
    else:
        # 複数年の場合は、各年の頻度をマージ
        merged_freq: Dict[str, int] = {}
        for year in selected_years:
            year_freq = cache.get(year, {})
            for word, count in year_freq.items():
                merged_freq[word] = merged_freq.get(word, 0) + count
        return merged_freq


# サイドバー
with st.sidebar:
    st.title(i18n.get("app_title"))

    # 言語選択
    language_option: str = st.selectbox(
        i18n.get("language"),
        options=["日本語", "English"],
        index=0 if st.session_state.language == "ja" else 1,
    )

    if language_option == "日本語" and st.session_state.language != "ja":
        st.session_state.language = "ja"
        i18n.set_language("ja")
        st.rerun()
    elif language_option == "English" and st.session_state.language != "en":
        st.session_state.language = "en"
        i18n.set_language("en")
        st.rerun()

    # ファイルアップロード
    uploaded_file: UploadedFile | None = st.file_uploader(
        i18n.get("load_file"),
        type=["json", "csv"],
    )

    if uploaded_file is not None:
        # 既に同じファイルが読み込まれている場合はスキップ
        if st.session_state.uploaded_filename != uploaded_file.name:
            load_data(uploaded_file)

    # アップロード済みファイル名を表示（言語切替後も表示を維持）
    if st.session_state.uploaded_filename is not None:
        st.caption(f"📄 {st.session_state.uploaded_filename}")

    # Sudachiモード選択
    if st.session_state.preprocessed_df is not None:
        st.markdown("---")
        st.subheader(i18n.get("morphological_analysis_settings"))

        # モード選択の説明
        with st.expander(i18n.get("sudachi_mode_about"), expanded=False):
            st.markdown(i18n.get("sudachi_mode_description"))

        # モードオプションを多言語化
        mode_options = [
            i18n.get("sudachi_mode_a"),
            i18n.get("sudachi_mode_b"),
            i18n.get("sudachi_mode_c"),
        ]

        sudachi_mode_option = st.radio(
            i18n.get("sudachi_mode_label"),
            options=mode_options,
            index=["A", "B", "C"].index(st.session_state.sudachi_mode),
            horizontal=True,
            key="sudachi_mode_radio",
        )

        # モードの変更を検出
        # 選択されたオプションからモード文字を抽出
        mode_index = mode_options.index(sudachi_mode_option)
        new_mode = ["A", "B", "C"][mode_index]

        if new_mode != st.session_state.sudachi_mode:
            st.session_state.sudachi_mode = new_mode
            # データが読み込まれている場合は再解析
            if st.session_state.preprocessed_df is not None:
                with st.spinner(i18n.get("sudachi_mode_changing")):
                    text_analyzer = TextAnalyzer(mode=new_mode)
                    st.session_state.word_analysis_cache = _build_word_analysis_cache(
                        st.session_state.preprocessed_df, text_analyzer
                    )
                st.success(i18n.get("sudachi_mode_changed", mode=new_mode))
                st.rerun()

    # グローバル年フィルタ
    if st.session_state.preprocessed_df is not None:
        st.markdown("---")
        st.subheader(i18n.get("year_filter_label"))

        # 利用可能な年を取得
        available_years: List[int] = TimeSeriesAnalyzer.get_available_years(
            st.session_state.preprocessed_df
        )

        # 全期間チェックボックス
        use_all_years = st.checkbox(
            i18n.get("all_years"),
            value=st.session_state.applied_use_all_years,
            key="all_years_cb",
        )

        # チェックボックスの状態変化を検出
        if use_all_years != st.session_state.applied_use_all_years:
            if use_all_years:
                # 全期間ONの場合
                st.session_state.applied_use_all_years = True
                st.session_state.applied_selected_years = []
            else:
                # 全期間OFFの場合、最新年を自動選択
                st.session_state.applied_use_all_years = False
                if available_years:
                    latest_year = max(available_years)
                    st.session_state.applied_selected_years = [latest_year]
            st.rerun()

        # 年選択チェックボックスの表示
        if not st.session_state.applied_use_all_years:
            st.write("年を選択:")

            # 一行に3個ずつ並べるレイアウト
            for i in range(0, len(available_years), 3):
                cols = st.columns(3)
                for j, year in enumerate(available_years[i:i+3]):
                    with cols[j]:
                        # この年が選択されているかチェック
                        is_selected = year in st.session_state.applied_selected_years
                        st.checkbox(
                            str(year),
                            value=is_selected,
                            key=f"year_cb_{year}",
                        )

            # 年選択の変化を検出
            selected = []
            for year in available_years:
                year_key = f"year_cb_{year}"
                if st.session_state.get(year_key, False):
                    selected.append(year)

            # 選択状態が変化した場合
            if selected != st.session_state.applied_selected_years:
                if selected:
                    # 年が選択されている場合
                    st.session_state.applied_use_all_years = False
                    st.session_state.applied_selected_years = selected
                else:
                    # 何も選択されていない場合は全期間に戻す
                    st.session_state.applied_use_all_years = True
                    st.session_state.applied_selected_years = []
                st.rerun()
        else:
            # 全期間選択時のヘルプテキスト
            st.caption("💡 上のチェックを外すと、特定の年を選択してフィルタリングできます")

    # 統計情報表示
    if st.session_state.preprocessed_df is not None:
        # フィルタ適用後のデータで統計を計算
        filtered_df = st.session_state.preprocessed_df
        if not st.session_state.applied_use_all_years and st.session_state.applied_selected_years:
            filtered_df = filtered_df.filter(
                pl.col("created_year").is_in(st.session_state.applied_selected_years)
            )

        stats: Dict[str, Any] = StatisticsAnalyzer.get_basic_stats(filtered_df)
        st.markdown("---")
        st.metric(i18n.get("bookmarks"), stats["total_bookmarks"])
        st.metric(i18n.get("folders"), stats["total_folders"])
        st.metric(i18n.get("avg_depth"), f"{stats['avg_hierarchy_depth']:.1f}")

# メインエリア
if st.session_state.preprocessed_df is None:
    st.info(i18n.get("welcome_message"))
else:
    # タブ作成
    tabs: Sequence[DeltaGenerator] = st.tabs(
        [
            i18n.get("browser_dist"),
            i18n.get("folder_dist"),
            i18n.get("domain_dist"),
            i18n.get("monthly_trend"),
            i18n.get("yearly_trend"),
            i18n.get("weekday_pattern"),
            i18n.get("hour_pattern"),
            i18n.get("weekday_hour_heatmap"),
            i18n.get("hierarchy_treemap"),
            i18n.get("folder_tree"),
            i18n.get("wordcloud"),
            i18n.get("word_ranking"),
        ]
    )

    # グローバル年フィルタを適用（適用済みのフィルタを使用）
    df = st.session_state.preprocessed_df
    use_all_years = st.session_state.applied_use_all_years
    selected_years: List[int] = st.session_state.applied_selected_years

    if not use_all_years:
        # 年フィルタを適用
        if selected_years:
            df = df.filter(pl.col("created_year").is_in(selected_years))

    # タイトルサフィックスを作成
    title_suffix = ""
    if not use_all_years and selected_years:
        year_str: str = "、".join([f"{y}年" for y in sorted(selected_years)])
        title_suffix: str = f": {year_str}"

    # ブラウザ分布
    with tabs[0]:
        st.subheader(i18n.get("browser_distribution_title") + title_suffix)
        browser_dist = StatisticsAnalyzer.get_browser_distribution(df)
        # 降順でソート
        browser_dist: pl.DataFrame = browser_dist.sort("count", descending=True)

        fig: Figure = PlotlyCharts.create_bar_chart(
            browser_dist,
            "Web Browser",
            "count",
            i18n.get("browser_distribution_title") + title_suffix,
            orientation="v",
            show_values=True,
            show_percentage=True,
        )
        st.plotly_chart(fig, width="stretch")

    # フォルダ分布
    with tabs[1]:
        st.subheader(i18n.get("folder_distribution_title", n="") + title_suffix)

        # 設定パネル
        col1, col2 = st.columns([3, 1])
        with col2:
            top_n_folder = st.number_input(
                i18n.get("top_n_label"),
                min_value=5,
                max_value=100,
                value=15,
                step=5,
                key="folder_top_n",
            )

        folder_dist: pl.DataFrame = StatisticsAnalyzer.get_folder_distribution(
            df, top_n=top_n_folder
        )
        # 降順でソート（横向き棒グラフは下から上なので、昇順にして上位が上に来るようにする）
        folder_dist = folder_dist.sort("count", descending=False)

        fig = PlotlyCharts.create_bar_chart(
            folder_dist,
            "Folder Name",
            "count",
            i18n.get("folder_distribution_title", n=top_n_folder) + title_suffix,
            orientation="h",
            show_values=True,
            show_percentage=False,
        )
        st.plotly_chart(fig, width="stretch")

    # ドメイン分布
    with tabs[2]:
        st.subheader(i18n.get("domain_distribution_title", n="") + title_suffix)

        # 設定パネル
        col1, col2 = st.columns([3, 1])
        with col2:
            top_n_domain = st.number_input(
                i18n.get("top_n_label"),
                min_value=5,
                max_value=100,
                value=15,
                step=5,
                key="domain_top_n",
            )

        domain_dist: pl.DataFrame = StatisticsAnalyzer.get_domain_distribution(
            df, top_n=top_n_domain
        )
        # 降順でソート（横向き棒グラフは下から上なので、昇順にして上位が上に来るようにする）
        domain_dist = domain_dist.sort("count", descending=False)

        fig = PlotlyCharts.create_bar_chart(
            domain_dist,
            "domain",
            "count",
            i18n.get("domain_distribution_title", n=top_n_domain) + title_suffix,
            orientation="h",
            show_values=True,
            show_percentage=True,
        )
        st.plotly_chart(fig, width="stretch")

    # 月次推移
    with tabs[3]:
        # サブヘッダー：年フィルタ適用時は「月次ブックマーク作成推移」のみ
        if not use_all_years and selected_years:
            st.subheader("月次ブックマーク作成推移" + title_suffix)
        else:
            st.subheader(i18n.get("monthly_trend_title_all") + title_suffix)

        # 年選択（ラジオボタン） - 年フィルタが適用されている場合は「全期間」を除外
        available_years_monthly = TimeSeriesAnalyzer.get_available_years(df)
        if not use_all_years and selected_years:
            # 年フィルタが適用されている場合は「全期間」オプションなし
            year_options: List[str] = [str(y) for y in available_years_monthly]
        else:
            year_options = [i18n.get("all_years")] + [str(y) for y in available_years_monthly]

        selected_year_str = st.radio(
            i18n.get("year_filter_label"),
            options=year_options,
            horizontal=True,
            key="monthly_year",
        )

        selected_year: Optional[int] = None
        if selected_year_str != i18n.get("all_years"):
            selected_year = int(selected_year_str)

        monthly_counts: pl.DataFrame = TimeSeriesAnalyzer.get_monthly_counts(df, year=selected_year)

        # 年-月ラベルを作成
        monthly_counts = monthly_counts.with_columns(
            [
                (
                    pl.col("created_year").cast(pl.Utf8)
                    + "-"
                    + pl.col("created_month").cast(pl.Utf8).str.zfill(2)
                ).alias("year_month")
            ]
        )

        # グラフタイトル：年フィルタ適用時は括弧部分を含めない
        if not use_all_years and selected_years:
            # 年フィルタ適用時は括弧なし
            title = "月次ブックマーク作成推移"
        else:
            # 通常時
            title: str = (
                i18n.get("monthly_trend_title", year=selected_year)
                if selected_year
                else i18n.get("monthly_trend_title_all")
            )

        fig = PlotlyCharts.create_line_chart(
            monthly_counts,
            "year_month",
            "count",
            title + title_suffix,
            show_markers=True,
            show_values=False,
        )
        st.plotly_chart(fig, width="stretch")

    # 年次推移 - 全期間選択時のみ表示
    if use_all_years:
        with tabs[4]:
            st.subheader(i18n.get("yearly_trend_title"))

            yearly_counts: pl.DataFrame = TimeSeriesAnalyzer.get_yearly_counts(df)

            fig = PlotlyCharts.create_line_chart(
                yearly_counts,
                "created_year",
                "count",
                i18n.get("yearly_trend_title"),
                show_markers=True,
                show_values=True,
            )
            st.plotly_chart(fig, width="stretch")
    else:
        with tabs[4]:
            st.info("年次推移は全期間を選択した場合のみ表示されます。")

    # 曜日パターン
    with tabs[5]:
        st.subheader(i18n.get("weekday_pattern_title") + title_suffix)

        weekday_dist = TimeSeriesAnalyzer.get_weekday_distribution(df)

        # 多言語対応の曜日名に置き換え
        weekday_names: List[str] = i18n.get_weekday_names()
        weekday_dist: pl.DataFrame = weekday_dist.with_columns(
            [
                pl.col("created_weekday")
                .map_elements(
                    lambda x: weekday_names[x] if 0 <= x < 7 else "Unknown",
                    return_dtype=pl.Utf8,
                )
                .alias("weekday_name")
            ]
        )

        fig = PlotlyCharts.create_bar_chart(
            weekday_dist,
            "weekday_name",
            "count",
            i18n.get("weekday_pattern_title") + title_suffix,
            show_values=True,
        )
        st.plotly_chart(fig, width="stretch")

    # 時間パターン
    with tabs[6]:
        st.subheader(i18n.get("hour_pattern_title") + title_suffix)

        hourly_dist = TimeSeriesAnalyzer.get_hourly_distribution(df)

        # すべての時間（0-23）を確保し、欠損値は0で埋める
        all_hours = pl.DataFrame({"created_hour": list(range(24))})
        hourly_dist: pl.DataFrame = all_hours.join(
            hourly_dist, on="created_hour", how="left"
        ).fill_null(0)

        fig = PlotlyCharts.create_bar_chart(
            hourly_dist,
            "created_hour",
            "count",
            i18n.get("hour_pattern_title") + title_suffix,
            show_values=True,  # すべての棒に数値を表示
        )
        st.plotly_chart(fig, width="stretch")

    # 曜日-時間ヒートマップ
    with tabs[7]:
        st.subheader(i18n.get("weekday_hour_heatmap_title") + title_suffix)

        heatmap_data: Dict[str, Any] = TimeSeriesAnalyzer.get_weekday_hour_heatmap(df)

        fig = PlotlyCharts.create_heatmap(
            heatmap_data,
            i18n.get("weekday_hour_heatmap_title") + title_suffix,
            colorscale="YlOrRd",
        )
        st.plotly_chart(fig, width="stretch")

    # 階層ツリーマップ
    with tabs[8]:
        st.subheader(i18n.get("hierarchy_treemap_title") + title_suffix)

        # 設定パネル
        col1, col2 = st.columns([3, 1])

        with col2:
            treemap_mode = st.radio(
                i18n.get("treemap_mode_label"),
                options=[
                    i18n.get("treemap_hierarchical"),
                    i18n.get("treemap_grouped"),
                ],
                key="treemap_mode",
            )

            treemap_height = st.slider(
                i18n.get("height_label"),
                min_value=400,
                max_value=1200,
                value=600,
                step=100,
                key="treemap_height",
            )

        hierarchical: bool = treemap_mode == i18n.get("treemap_hierarchical")

        treemap_data: Dict[str, Any] = HierarchyAnalyzer.build_treemap_data(
            df,
            max_depth=None,
            hierarchical=hierarchical,
        )

        fig = PlotlyCharts.create_treemap(
            treemap_data,
            i18n.get("hierarchy_treemap_title") + title_suffix,
            height=treemap_height,
        )
        st.plotly_chart(fig, width="stretch")

    # フォルダツリー
    with tabs[9]:
        st.subheader(i18n.get("folder_tree_title") + title_suffix)

        tree: Dict[str, Any] = HierarchyAnalyzer.get_hierarchy_tree_structure(df)
        tree_text: str = HierarchyAnalyzer.format_tree_text(tree)

        st.code(tree_text, language=None)

    # ワードクラウド
    with tabs[10]:
        st.subheader(i18n.get("wordcloud_title") + title_suffix)

        if st.session_state.word_analysis_cache is None:
            st.warning(i18n.get("no_words_found"))
        else:
            # キャッシュから該当する年の単語頻度を取得
            word_freq = _get_word_freq_from_cache(
                st.session_state.word_analysis_cache, use_all_years, selected_years
            )

            if not word_freq:
                st.warning(i18n.get("no_words_found"))
            else:
                # 設定パネル
                col1, col2 = st.columns([3, 1])

                with col2:
                    # カラーマップ選択
                    colormap_options = WordCloudGenerator.get_available_colormaps()
                    selected_colormap = st.selectbox(
                        i18n.get("colormap_label"),
                        options=list(colormap_options.keys()),
                        format_func=lambda x: colormap_options[x],
                        index=0,
                        key="wordcloud_colormap",
                    )

                    # 最大単語数
                    max_words = st.slider(
                        i18n.get("max_words_label"),
                        min_value=20,
                        max_value=200,
                        value=100,
                        step=10,
                        key="wordcloud_max_words",
                    )

                # ワードクラウド生成（キャッシュから即座に生成）
                wc_generator = WordCloudGenerator()
                fig = wc_generator.generate_wordcloud_figure(
                    word_freq,
                    width=1200,
                    height=600,
                    background_color="white",
                    colormap=selected_colormap,
                    max_words=max_words,
                    title=i18n.get("wordcloud_title") + title_suffix,
                )
                st.pyplot(fig)

    # 単語ランキング
    with tabs[11]:
        st.subheader(i18n.get("word_ranking_title", n="") + title_suffix)

        if st.session_state.word_analysis_cache is None:
            st.warning(i18n.get("no_words_found"))
        else:
            # キャッシュから該当する年の単語頻度を取得
            word_freq = _get_word_freq_from_cache(
                st.session_state.word_analysis_cache, use_all_years, selected_years
            )

            if not word_freq:
                st.warning(i18n.get("no_words_found"))
            else:
                # 設定パネル
                col1, col2 = st.columns([3, 1])

                with col2:
                    top_n_words = st.number_input(
                        i18n.get("top_n_label"),
                        min_value=5,
                        max_value=200,
                        value=100,
                        step=5,
                        key="word_ranking_top_n",
                    )

                # 上位N件を取得
                top_words_df = TextAnalyzer.get_top_words(word_freq, top_n=top_n_words)

                if len(top_words_df) > 0:
                    # 降順でソート
                    top_words_df = top_words_df.sort("count", descending=True)

                    # 順位、パーセンテージを追加
                    total_count = sum(word_freq.values())
                    top_words_df = top_words_df.with_columns(
                        [
                            pl.Series("rank", list(range(1, len(top_words_df) + 1))),
                            (pl.col("count") / total_count * 100).alias("percentage"),
                        ]
                    )

                    # カラムの順序を変更
                    top_words_df = top_words_df.select(["rank", "word", "count", "percentage"])

                    # マークダウン表として表示
                    st.markdown("### " + i18n.get("word_ranking_title", n=top_n_words))

                    # DataFrameをPandasに変換して表示
                    display_df = top_words_df.to_pandas()

                    # パーセンテージをフォーマット（カラム名変更前に実行）
                    display_df["percentage"] = display_df["percentage"].apply(lambda x: f"{x:.2f}%")

                    # カラム名を翻訳
                    display_df.columns = [
                        i18n.get("rank"),
                        i18n.get("word"),
                        i18n.get("count"),
                        i18n.get("percentage"),
                    ]

                    st.dataframe(display_df, width="stretch", hide_index=True)

                    # ダウンロードボタン
                    st.markdown("---")
                    col_csv, col_json = st.columns(2)

                    # CSV/JSON用にパーセンテージを数値のまま保持したDataFrameを作成
                    download_df = top_words_df.with_columns([pl.col("percentage").round(2)])

                    with col_csv:
                        csv_data = download_df.write_csv()
                        st.download_button(
                            label="📥 CSV ダウンロード",
                            data=csv_data,
                            file_name=f"word_ranking_{title_suffix.replace(':', '').replace(' ', '_')}.csv",
                            mime="text/csv",
                        )

                    with col_json:
                        json_data = download_df.write_json()
                        st.download_button(
                            label="📥 JSON ダウンロード",
                            data=json_data,
                            file_name=f"word_ranking_{title_suffix.replace(':', '').replace(' ', '_')}.json",
                            mime="application/json",
                        )
                else:
                    st.warning(i18n.get("no_words_found"))
