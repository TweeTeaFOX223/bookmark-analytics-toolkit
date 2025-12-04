"""ブックマークデータの統計分析モジュール"""

from typing import Dict, Any
import polars as pl


class StatisticsAnalyzer:
    """ブックマーク統計を計算する分析クラス"""

    @staticmethod
    def get_basic_stats(df: pl.DataFrame) -> Dict[str, Any]:
        """
        ブックマークコレクションの基本統計を取得

        Args:
            df: 前処理済みブックマークデータフレーム

        Returns:
            基本統計の辞書
        """
        total_bookmarks: int = len(df)
        unique_folders: int = df["Folder Path"].n_unique()

        # 日付範囲
        date_range_start: Any = df["created_datetime"].min()
        date_range_end: Any = df["created_datetime"].max()

        # ブラウザ分布
        browsers: pl.DataFrame = df.group_by("Web Browser").agg(
            pl.count().alias("count")
        )
        browser_dict: Dict[str, int] = dict(
            zip(browsers["Web Browser"].to_list(), browsers["count"].to_list())
        )

        # 階層深さの統計
        avg_hierarchy_depth: float = float(df["hierarchy_level"].mean() or 0)
        max_hierarchy_depth: int = int(df["hierarchy_level"].max() or 0)
        min_hierarchy_depth: int = int(df["hierarchy_level"].min() or 0)

        # 変更済みブックマーク
        total_modified: int = int(df["is_modified"].sum() or 0)

        return {
            "total_bookmarks": total_bookmarks,
            "total_folders": unique_folders,
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
            "browsers": browser_dict,
            "avg_hierarchy_depth": avg_hierarchy_depth,
            "max_hierarchy_depth": max_hierarchy_depth,
            "min_hierarchy_depth": min_hierarchy_depth,
            "total_modified": total_modified,
        }

    @staticmethod
    def get_browser_distribution(df: pl.DataFrame) -> pl.DataFrame:
        """
        ブラウザ別のブックマーク数を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            ブラウザカウントのデータフレーム
        """
        return (
            df.group_by("Web Browser")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
        )

    @staticmethod
    def get_folder_distribution(df: pl.DataFrame, top_n: int = 20) -> pl.DataFrame:
        """
        ブックマーク数で上位N個のフォルダを取得

        Args:
            df: 前処理済みデータフレーム
            top_n: 返す上位フォルダの数

        Returns:
            フォルダカウントのデータフレーム
        """
        return (
            df.group_by("Folder Name")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
            .head(top_n)
        )

    @staticmethod
    def get_domain_distribution(df: pl.DataFrame, top_n: int = 20) -> pl.DataFrame:
        """
        ブックマーク数で上位N個のドメインを取得

        Args:
            df: 前処理済みデータフレーム
            top_n: 返す上位ドメインの数

        Returns:
            ドメインカウントのデータフレーム
        """
        return (
            df.filter(pl.col("domain") != "")
            .group_by("domain")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
            .head(top_n)
        )

    @staticmethod
    def get_hierarchy_depth_distribution(df: pl.DataFrame) -> pl.DataFrame:
        """
        階層深さの分布を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            階層レベルカウントのデータフレーム
        """
        return (
            df.group_by("hierarchy_level")
            .agg(pl.count().alias("count"))
            .sort("hierarchy_level")
        )

    @staticmethod
    def get_title_length_stats(df: pl.DataFrame) -> Dict[str, float]:
        """
        ブックマークタイトルの長さに関する統計を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            タイトル長統計の辞書
        """
        return {
            "mean_length": float(df["title_length"].mean() or 0),
            "median_length": float(df["title_length"].median() or 0),
            "max_length": float(df["title_length"].max() or 0),
            "min_length": float(df["title_length"].min() or 0),
        }

    @staticmethod
    def get_root_folder_distribution(df: pl.DataFrame) -> pl.DataFrame:
        """
        ルートフォルダ別のブックマーク分布を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            ルートフォルダカウントのデータフレーム
        """
        return (
            df.group_by("root_folder")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
        )
