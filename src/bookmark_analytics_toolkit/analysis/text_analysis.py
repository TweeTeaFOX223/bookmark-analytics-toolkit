"""
テキスト分析モジュール - SudachiPyを使用した形態素解析機能

このモジュールは、ブックマークのタイトルテキストを形態素解析し、
単語の出現頻度やワードクラウドのためのデータを生成します。
"""

from typing import Dict, List, Tuple
import polars as pl
from sudachipy import tokenizer
from sudachipy import dictionary


class TextAnalyzer:
    """
    SudachiPyを使用したテキスト分析クラス

    ブックマークのタイトルから単語を抽出し、
    出現回数のカウントや品詞フィルタリングを行います。
    """

    def __init__(self, mode: str = "C") -> None:
        """
        SudachiPy Tokenizerを初期化

        Args:
            mode: 分割モード ("A", "B", "C")
                - A: 短単位（最も細かい分割）
                - B: 中単位（バランスの取れた分割）
                - C: 長単位（最も長い分割）
        """
        # SudachiDict-fullを使用してトークナイザーを作成
        self.tokenizer_obj = dictionary.Dictionary(dict="full").create()
        # 分割モードを設定
        self.set_mode(mode)

    def set_mode(self, mode: str) -> None:
        """
        分割モードを設定

        Args:
            mode: 分割モード ("A", "B", "C")
        """
        if mode == "A":
            self.mode = tokenizer.Tokenizer.SplitMode.A
        elif mode == "B":
            self.mode = tokenizer.Tokenizer.SplitMode.B
        else:  # "C" or default
            self.mode = tokenizer.Tokenizer.SplitMode.C

    @staticmethod
    def _is_valid_word(word: str, pos: str) -> bool:
        """
        単語が分析対象として有効かどうかを判定

        Args:
            word: 単語
            pos: 品詞情報

        Returns:
            有効な単語の場合True
        """
        # 1文字の単語は除外
        if len(word) <= 1:
            return False

        # 品詞フィルタ: 名詞、動詞、形容詞のみを対象
        valid_pos = ["名詞", "動詞", "形容詞"]
        if not any(pos.startswith(p) for p in valid_pos):
            return False

        # 除外する名詞のサブタイプ
        exclude_subtypes = ["非自立", "代名詞", "数"]
        if any(subtype in pos for subtype in exclude_subtypes):
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

            # 形態素解析
            tokens = self.tokenizer_obj.tokenize(text, self.mode)

            for token in tokens:
                # 表層形（原形ではなく表層形を使用）
                word = token.surface()
                # 品詞情報を取得（カンマ区切りの文字列）
                pos = token.part_of_speech()[0]  # 品詞の第1要素（大分類）

                # 有効な単語のみを追加
                if self._is_valid_word(word, pos):
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
