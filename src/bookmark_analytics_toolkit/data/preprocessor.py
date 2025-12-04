"""ブックマーク分析用のデータ前処理"""

from urllib.parse import urlparse
from typing import Optional

import polars as pl


class BookmarkPreprocessor:
    """派生カラム生成を伴うブックマークデータの前処理クラス"""

    @staticmethod
    def preprocess(df: pl.DataFrame) -> pl.DataFrame:
        """
        すべての変換を含むブックマークデータの前処理

        Args:
            df: 生のブックマークデータフレーム

        Returns:
            派生カラム付きの前処理済みデータフレーム
        """
        # 日時カラムをパース
        df = BookmarkPreprocessor._parse_datetime(df)

        # 派生カラムを生成
        df = BookmarkPreprocessor._add_hierarchy_columns(df)
        df = BookmarkPreprocessor._add_temporal_columns(df)
        df = BookmarkPreprocessor._add_url_columns(df)
        df = BookmarkPreprocessor._add_metadata_columns(df)

        return df

    @staticmethod
    def _parse_datetime(df: pl.DataFrame) -> pl.DataFrame:
        """日時文字列を日時オブジェクトにパース"""
        # 両方のフォーマットを処理: "YYYY/MM/DD H:MM:SS" と "YYYY/MM/DD HH:MM:SS"
        df = df.with_columns(
            [
                pl.col("Created Time")
                .str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False)
                .alias("created_datetime"),
                pl.when(pl.col("Modified Time") != "")
                .then(
                    pl.col("Modified Time").str.strptime(
                        pl.Datetime, "%Y/%m/%d %H:%M:%S", strict=False
                    )
                )
                .otherwise(None)
                .alias("modified_datetime"),
            ]
        )

        return df

    @staticmethod
    def _add_hierarchy_columns(df: pl.DataFrame) -> pl.DataFrame:
        """階層関連の派生カラムを追加"""
        df = df.with_columns(
            [
                # フォルダパスを分割して階層レベルを計算
                pl.col("Folder Path")
                .str.split("\\\\")
                .alias("folder_path_parts"),
            ]
        ).with_columns(
            [
                pl.col("folder_path_parts").list.len().alias("hierarchy_level"),
                # ルートフォルダ(最初の要素)を取得
                pl.col("folder_path_parts").list.first().alias("root_folder"),
            ]
        )

        return df

    @staticmethod
    def _add_temporal_columns(df: pl.DataFrame) -> pl.DataFrame:
        """時間ベースの派生カラムを追加"""
        df = df.with_columns(
            [
                pl.col("created_datetime").dt.year().alias("created_year"),
                pl.col("created_datetime").dt.month().alias("created_month"),
                pl.col("created_datetime").dt.day().alias("created_day"),
                # Polarsのweekdayは1=月曜, 7=日曜なので、0=月曜, 6=日曜に変換
                (pl.col("created_datetime").dt.weekday() - 1).alias("created_weekday"),
                pl.col("created_datetime").dt.hour().alias("created_hour"),
                pl.col("created_datetime").dt.date().alias("created_date"),
            ]
        )

        return df

    @staticmethod
    def _add_url_columns(df: pl.DataFrame) -> pl.DataFrame:
        """URLベースの派生カラムを追加"""

        def extract_domain(url: str) -> str:
            """URLからドメインを抽出"""
            try:
                parsed = urlparse(url)
                return parsed.netloc
            except Exception:
                return ""

        # Polarsのmap_elementsを使用してURLをパース
        df = df.with_columns(
            [
                pl.col("URL")
                .map_elements(extract_domain, return_dtype=pl.Utf8)
                .alias("domain"),
            ]
        )

        return df

    @staticmethod
    def _add_metadata_columns(df: pl.DataFrame) -> pl.DataFrame:
        """メタデータ派生カラムを追加"""
        df = df.with_columns(
            [
                pl.col("modified_datetime").is_not_null().alias("is_modified"),
                pl.col("Title").str.len_chars().alias("title_length"),
            ]
        )

        return df

    @staticmethod
    def filter_by_date_range(
        df: pl.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pl.DataFrame:
        """
        日付範囲でブックマークをフィルタ

        Args:
            df: 前処理済みデータフレーム
            start_date: 開始日 ISO形式 (YYYY-MM-DD)
            end_date: 終了日 ISO形式 (YYYY-MM-DD)

        Returns:
            フィルタ済みデータフレーム
        """
        if start_date:
            df = df.filter(pl.col("created_date") >= start_date)
        if end_date:
            df = df.filter(pl.col("created_date") <= end_date)

        return df

    @staticmethod
    def filter_by_folder(df: pl.DataFrame, folder_path: str) -> pl.DataFrame:
        """
        フォルダパスでブックマークをフィルタ (部分一致)

        Args:
            df: 前処理済みデータフレーム
            folder_path: フィルタするフォルダパス

        Returns:
            フィルタ済みデータフレーム
        """
        return df.filter(pl.col("Folder Path").str.contains(folder_path))

    @staticmethod
    def filter_by_browser(df: pl.DataFrame, browser: str) -> pl.DataFrame:
        """
        ブラウザ名でブックマークをフィルタ

        Args:
            df: 前処理済みデータフレーム
            browser: ブラウザ名

        Returns:
            フィルタ済みデータフレーム
        """
        return df.filter(pl.col("Web Browser") == browser)

    @staticmethod
    def search(df: pl.DataFrame, query: str) -> pl.DataFrame:
        """
        タイトルまたはURLでブックマークを検索

        Args:
            df: 前処理済みデータフレーム
            query: 検索クエリ文字列

        Returns:
            マッチしたブックマークのフィルタ済みデータフレーム
        """
        return df.filter(
            pl.col("Title").str.to_lowercase().str.contains(query.lower())
            | pl.col("URL").str.to_lowercase().str.contains(query.lower())
        )
