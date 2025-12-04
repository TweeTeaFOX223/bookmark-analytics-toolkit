"""JSONとCSVブックマークファイルのデータローダー"""

import json
from pathlib import Path
from typing import Literal, Optional

import polars as pl


class BookmarkLoader:
    """JSONまたはCSVファイルからブックマークデータを読み込むクラス"""

    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """
        BOMを読み取るか一般的なエンコーディングを試してファイルエンコーディングを検出

        Args:
            file_path: ファイルパス

        Returns:
            検出されたエンコーディング名
        """
        # 最初の数バイトを読み取ってBOMをチェック
        with open(file_path, "rb") as f:
            raw_data: bytes = f.read(4)

        # BOM (Byte Order Mark) をチェック
        if raw_data.startswith(b"\xff\xfe\x00\x00"):
            return "utf-32-le"
        elif raw_data.startswith(b"\x00\x00\xfe\xff"):
            return "utf-32-be"
        elif raw_data.startswith(b"\xff\xfe"):
            return "utf-16-le"
        elif raw_data.startswith(b"\xfe\xff"):
            return "utf-16-be"
        elif raw_data.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"

        # 各種エンコーディングを試す
        encodings: list[str] = [
            "utf-8",
            "utf-16",
            "shift_jis",
            "cp932",
            "euc_jp",
            "iso-2022-jp",
            "latin1",
        ]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue

        # 何も動作しない場合はutf-8をデフォルトに
        return "utf-8"

    @staticmethod
    def load(
        file_path: str | Path, file_type: Optional[Literal["json", "csv"]] = None,
    ) -> pl.DataFrame:
        """
        ファイルからブックマークデータを読み込み

        Args:
            file_path: ブックマークファイルのパス
            file_type: ファイルタイプ ('json' または 'csv')。Noneの場合は拡張子から推測

        Returns:
            ブックマークデータを含むPolarsデータフレーム

        Raises:
            ValueError: ファイルタイプがサポートされていないか推測できない場合
            FileNotFoundError: ファイルが存在しない場合
        """
        path: Path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 指定されていない場合は拡張子からファイルタイプを推測
        if file_type is None:
            file_type_str: str = path.suffix.lower().lstrip(".")
            if file_type_str not in ["json", "csv"]:
                raise ValueError(f"Unsupported file extension: {path.suffix}")
            file_type = file_type_str  # type: ignore

        # ファイルタイプに基づいてデータを読み込み
        if file_type == "json":
            return BookmarkLoader._load_json(path)
        elif file_type == "csv":
            return BookmarkLoader._load_csv(path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _load_json(path: Path) -> pl.DataFrame:
        """JSONファイルを読み込んでPolarsデータフレームとして返す"""
        # エンコーディングを検出
        encoding: str = BookmarkLoader.detect_encoding(path)

        # 試すエンコーディングのリスト
        encodings_to_try: list[str] = [
            encoding,
            "utf-8-sig",
            "utf-8",
            "utf-16",
            "utf-16-le",
            "utf-16-be",
        ]

        data: Optional[list] = None
        last_error: Optional[Exception] = None

        for enc in encodings_to_try:
            try:
                with open(path, "r", encoding=enc) as f:
                    content: str = f.read()
                    # 先頭にBOMがあれば削除
                    if content.startswith("\ufeff"):
                        content = content[1:]
                    data = json.loads(content)
                    break
            except (UnicodeDecodeError, json.JSONDecodeError, LookupError) as e:
                last_error = e
                continue

        # すべてのエンコーディングが失敗した場合、エラーハンドリングでバイトとして読み取る
        if data is None:
            try:
                with open(path, "rb") as f:
                    raw_content: bytes = f.read()
                    # BOMバイトがあれば削除
                    if raw_content.startswith(b"\xef\xbb\xbf"):
                        raw_content = raw_content[3:]
                    elif raw_content.startswith(b"\xff\xfe"):
                        raw_content = raw_content[2:]
                    elif raw_content.startswith(b"\xfe\xff"):
                        raw_content = raw_content[2:]

                    # 複数のエンコーディングでデコードを試行
                    for enc in ["utf-8", "utf-16", "shift_jis", "cp932", "latin1"]:
                        try:
                            text: str = raw_content.decode(enc, errors="replace")
                            data = json.loads(text)
                            break
                        except (UnicodeDecodeError, json.JSONDecodeError):
                            continue
            except Exception as e:
                last_error = e

        if data is None:
            raise ValueError(f"Failed to parse JSON file: {last_error}")

        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of bookmark objects")

        return pl.DataFrame(data)

    @staticmethod
    def _load_csv(path: Path) -> pl.DataFrame:
        """CSVファイルを読み込んでPolarsデータフレームとして返す"""
        # エンコーディングを検出
        encoding: str = BookmarkLoader.detect_encoding(path)

        # 試すエンコーディングのリスト
        encodings_to_try: list[str] = [
            encoding,
            "utf-8-sig",
            "utf-8",
            "utf-16",
            "utf-16-le",
            "utf-16-be",
            "shift_jis",
            "cp932",
            "latin1",
        ]

        last_error: Optional[Exception] = None
        for enc in encodings_to_try:
            try:
                return pl.read_csv(path, encoding=enc)
            except Exception as e:
                last_error = e
                continue

        raise ValueError(
            f"Failed to read CSV file with any encoding. Last error: {last_error}"
        )

    @staticmethod
    def validate_schema(df: pl.DataFrame) -> bool:
        """
        データフレームが必要なカラムを持っているか検証

        Args:
            df: 検証するデータフレーム

        Returns:
            スキーマが有効な場合True

        Raises:
            ValueError: 必要なカラムが不足している場合
        """
        required_columns: set[str] = {
            "Title",
            "URL",
            "Folder Name",
            "Folder Path",
            "Position",
            "Created Time",
            "ID",
            "Guid",
            "Web Browser",
            "Bookmarks File",
        }

        existing_columns: set[str] = set(df.columns)
        missing_columns: set[str] = required_columns - existing_columns

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return True

    @staticmethod
    def get_preview(df: pl.DataFrame, n: int = 10) -> pl.DataFrame:
        """
        最初のn行のプレビューを取得

        Args:
            df: プレビューするデータフレーム
            n: 返す行数

        Returns:
            最初のn行のデータフレーム
        """
        return df.head(n)
