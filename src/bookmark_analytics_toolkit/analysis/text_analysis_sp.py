"""
SentencePieceを使用したテキスト分析モジュール

このモジュールは、ブックマークのタイトルテキストをSentencePieceで分割し、
単語の出現頻度やワードクラウドのためのデータを生成します。
"""

from typing import Dict, List, Tuple
import polars as pl
import sentencepiece as spm
from pathlib import Path
import tempfile
import urllib.request


class TextAnalyzerSP:
    """
    SentencePieceを使用したテキスト分析クラス

    ブックマークのタイトルから単語を抽出し、
    出現回数のカウントや品詞フィルタリングを行います。
    """

    def __init__(self, model_path: str = None) -> None:
        """
        SentencePiece Processorを初期化

        Args:
            model_path: SentencePieceモデルのパス。Noneの場合は日本語用モデルをダウンロード
        """
        self.sp: spm.SentencePieceProcessor = spm.SentencePieceProcessor()

        if model_path is None:
            # デフォルトの日本語モデルを使用
            model_path = self._get_japanese_model()

        self.sp.load(model_path)

    @staticmethod
    def _get_japanese_model() -> str:
        """
        日本語用SentencePieceモデルを取得

        Returns:
            モデルファイルのパス
        """
        # Wikipedia日本語モデルのURL（小サイズ）
        model_url = "https://github.com/google/sentencepiece/raw/master/data/ja.wiki.bpe.vs32000.model"

        # 一時ディレクトリにダウンロード
        temp_dir = Path(tempfile.gettempdir()) / "bookmark_analytics"
        temp_dir.mkdir(exist_ok=True)

        model_path = temp_dir / "ja.wiki.bpe.vs32000.model"

        # モデルが既にダウンロード済みかチェック
        if not model_path.exists():
            try:
                urllib.request.urlretrieve(model_url, model_path)
            except Exception as e:
                # ダウンロード失敗時は例外を発生
                raise RuntimeError(
                    f"SentencePieceモデルのダウンロードに失敗しました: {e}\n"
                    f"手動でダウンロードして、model_pathに指定してください。"
                )

        return str(model_path)

    @staticmethod
    def _is_valid_word(word: str) -> bool:
        """
        単語が分析対象として有効かどうかを判定

        Args:
            word: 単語

        Returns:
            有効な単語の場合True
        """
        # 1文字の単語は除外
        if len(word) <= 1:
            return False

        # 記号のみの単語を除外
        if word.strip() in ["▁", "�", " ", "\n", "\t"]:
            return False

        # SentencePieceの特殊記号を除外
        if word.startswith("▁▁"):
            return False

        # 数字のみの単語を除外
        if word.strip("▁").isdigit():
            return False

        return True

    def extract_words(self, texts: List[str]) -> List[str]:
        """
        テキストのリストから有効な単語を抽出

        Args:
            texts: ブックマークタイトルのリスト

        Returns:
            抽出された単語のリスト
        """
        words: List[str] = []

        for text in texts:
            if not text or not isinstance(text, str):
                continue

            # SentencePieceで分割
            pieces = self.sp.encode_as_pieces(text)

            for piece in pieces:
                # ▁（アンダースコア）を削除して正規化
                word = piece.replace("▁", "").strip()

                # 有効な単語のみを追加
                if word and self._is_valid_word(word):
                    words.append(word)

        return words

    def get_word_frequency(
        self, df: pl.DataFrame, title_column: str = "Title"
    ) -> Dict[str, int]:
        """
        DataFrameからブックマークタイトルを抽出し、単語の出現頻度を計算

        Args:
            df: ブックマークデータのDataFrame
            title_column: タイトルカラムの名前（デフォルト: "Title"）

        Returns:
            単語と出現回数の辞書
        """
        # タイトルカラムを取得
        if title_column not in df.columns:
            return {}

        titles: List[str] = df[title_column].to_list()

        # 単語を抽出
        words: List[str] = self.extract_words(titles)

        # 出現回数をカウント
        word_freq: Dict[str, int] = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        return word_freq

    @staticmethod
    def get_top_words(word_freq: Dict[str, int], top_n: int = 50) -> pl.DataFrame:
        """
        単語の出現回数から上位N件を取得

        Args:
            word_freq: 単語と出現回数の辞書
            top_n: 取得する上位件数

        Returns:
            word, count カラムを持つDataFrame（降順ソート済み）
        """
        # 辞書をリストに変換してソート
        sorted_words: List[Tuple[str, int]] = sorted(
            word_freq.items(), key=lambda x: x[1], reverse=True
        )

        # 上位N件を取得
        top_words = sorted_words[:top_n]

        # DataFrameに変換
        if not top_words:
            return pl.DataFrame({"word": [], "count": []})

        words, counts = zip(*top_words)
        return pl.DataFrame({"word": list(words), "count": list(counts)})

    def analyze_text(
        self, df: pl.DataFrame, title_column: str = "Title", top_n: int = 50
    ) -> Tuple[Dict[str, int], pl.DataFrame]:
        """
        テキスト分析の完全なパイプライン

        Args:
            df: ブックマークデータのDataFrame
            title_column: タイトルカラムの名前
            top_n: 取得する上位件数

        Returns:
            (全単語の出現頻度辞書, 上位N件のDataFrame)
        """
        word_freq = self.get_word_frequency(df, title_column)
        top_words_df = self.get_top_words(word_freq, top_n)

        return word_freq, top_words_df
