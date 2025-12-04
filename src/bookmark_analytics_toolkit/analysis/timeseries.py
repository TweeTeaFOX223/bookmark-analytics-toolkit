"""ブックマークデータの時系列分析モジュール"""

from typing import Dict, List, Any, Optional
import polars as pl


class TimeSeriesAnalyzer:
    """時系列パターン分析クラス"""

    @staticmethod
    def get_monthly_counts(
        df: pl.DataFrame, year: Optional[int] = None
    ) -> pl.DataFrame:
        """
        月次ブックマーク数を取得

        Args:
            df: 前処理済みデータフレーム
            year: 特定の年でフィルタ (Noneの場合は全期間)

        Returns:
            月次カウントのデータフレーム
        """
        filtered_df: pl.DataFrame = df
        if year is not None:
            filtered_df = df.filter(pl.col("created_year") == year)

        return (
            filtered_df.group_by(["created_year", "created_month"])
            .agg(pl.count().alias("count"))
            .sort(["created_year", "created_month"])
        )

    @staticmethod
    def get_yearly_counts(df: pl.DataFrame) -> pl.DataFrame:
        """
        年次ブックマーク数を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            年次カウントのデータフレーム
        """
        return (
            df.group_by("created_year")
            .agg(pl.count().alias("count"))
            .sort("created_year")
        )

    @staticmethod
    def get_daily_counts(df: pl.DataFrame) -> pl.DataFrame:
        """
        日次ブックマーク数を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            日次カウントのデータフレーム
        """
        return (
            df.group_by("created_date")
            .agg(pl.count().alias("count"))
            .sort("created_date")
        )

    @staticmethod
    def get_weekday_distribution(df: pl.DataFrame) -> pl.DataFrame:
        """
        曜日別ブックマーク分布を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            曜日カウントのデータフレーム (0=月曜, 6=日曜)
        """
        # 曜日でグループ化
        weekday_counts: pl.DataFrame = (
            df.group_by("created_weekday")
            .agg(pl.count().alias("count"))
            .sort("created_weekday")
        )

        # 曜日名を追加
        weekday_names: List[str] = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        # 安全に曜日名をマッピング
        def safe_weekday_name(weekday: int) -> str:
            """曜日インデックスから曜日名を安全に取得"""
            if 0 <= weekday < len(weekday_names):
                return weekday_names[weekday]
            return f"Unknown({weekday})"

        weekday_counts = weekday_counts.with_columns(
            [
                pl.col("created_weekday")
                .map_elements(safe_weekday_name, return_dtype=pl.Utf8)
                .alias("weekday_name")
            ]
        )

        return weekday_counts

    @staticmethod
    def get_hourly_distribution(df: pl.DataFrame) -> pl.DataFrame:
        """
        時間別ブックマーク分布を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            時間カウントのデータフレーム (0-23)
        """
        return (
            df.group_by("created_hour")
            .agg(pl.count().alias("count"))
            .sort("created_hour")
        )

    @staticmethod
    def get_weekday_hour_heatmap(df: pl.DataFrame) -> Dict[str, Any]:
        """
        曜日 vs 時間のヒートマップデータを取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            ヒートマップデータ構造の辞書
        """
        heatmap_data: pl.DataFrame = (
            df.group_by(["created_weekday", "created_hour"])
            .agg(pl.count().alias("count"))
            .sort(["created_weekday", "created_hour"])
        )

        # 7日 x 24時間の2次元配列を作成
        values: List[List[int]] = [[0 for _ in range(24)] for _ in range(7)]

        for row in heatmap_data.iter_rows(named=True):
            weekday: int = row["created_weekday"]
            hour: int = row["created_hour"]
            count: int = row["count"]

            # 曜日と時間が有効な範囲内か確認
            if 0 <= weekday < 7 and 0 <= hour < 24:
                values[weekday][hour] = count

        weekday_labels: List[str] = ["月", "火", "水", "木", "金", "土", "日"]
        hour_labels: List[str] = [f"{h:02d}時" for h in range(24)]

        return {"x_labels": hour_labels, "y_labels": weekday_labels, "values": values}

    @staticmethod
    def get_year_month_heatmap(df: pl.DataFrame) -> Dict[str, Any]:
        """
        年 vs 月のヒートマップデータを取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            ヒートマップデータ構造の辞書
        """
        heatmap_data: pl.DataFrame = (
            df.group_by(["created_year", "created_month"])
            .agg(pl.count().alias("count"))
            .sort(["created_year", "created_month"])
        )

        # ユニークな年と月を取得
        years: List[int] = sorted(df["created_year"].unique().to_list())
        months: List[int] = list(range(1, 13))

        # 2次元配列を作成
        values: List[List[int]] = [[0 for _ in range(12)] for _ in range(len(years))]

        for row in heatmap_data.iter_rows(named=True):
            year_idx: int = years.index(row["created_year"])
            month_idx: int = row["created_month"] - 1
            values[year_idx][month_idx] = row["count"]

        month_labels: List[str] = [
            "1月",
            "2月",
            "3月",
            "4月",
            "5月",
            "6月",
            "7月",
            "8月",
            "9月",
            "10月",
            "11月",
            "12月",
        ]
        year_labels: List[str] = [str(y) for y in years]

        return {"x_labels": month_labels, "y_labels": year_labels, "values": values}

    @staticmethod
    def get_cumulative_counts(df: pl.DataFrame) -> pl.DataFrame:
        """
        累積ブックマーク数を時系列で取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            累積カウント付きのデータフレーム
        """
        daily_counts: pl.DataFrame = (
            df.group_by("created_date")
            .agg(pl.count().alias("count"))
            .sort("created_date")
        )

        # 累積和を計算
        daily_counts = daily_counts.with_columns(
            [pl.col("count").cum_sum().alias("cumulative_count")]
        )

        return daily_counts

    @staticmethod
    def get_modified_bookmarks_timeline(df: pl.DataFrame) -> pl.DataFrame:
        """
        ブックマーク変更のタイムラインを取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            変更日ごとのカウントデータフレーム
        """
        modified_df: pl.DataFrame = df.filter(pl.col("is_modified"))

        if len(modified_df) == 0:
            return pl.DataFrame({"modified_date": [], "count": []})

        # modified_datetimeから日付を抽出
        modified_df = modified_df.with_columns(
            [pl.col("modified_datetime").dt.date().alias("modified_date")]
        )

        return (
            modified_df.group_by("modified_date")
            .agg(pl.count().alias("count"))
            .sort("modified_date")
        )

    @staticmethod
    def get_available_years(df: pl.DataFrame) -> List[int]:
        """
        データに含まれる年のリストを取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            年のリスト (ソート済み)
        """
        return sorted(df["created_year"].unique().to_list())
