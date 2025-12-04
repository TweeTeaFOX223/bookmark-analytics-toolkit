"""
ワードクラウド可視化モジュール

このモジュールは、単語の出現頻度からワードクラウド画像を生成し、
Streamlitで表示できる形式で提供します。
"""

from typing import Dict, Optional
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')  # バックエンドをAggに設定（GUI不要）
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import matplotlib.font_manager as fm


class WordCloudGenerator:
    """ワードクラウド生成クラス"""

    def __init__(self, font_path: Optional[str] = None) -> None:
        """
        ワードクラウドジェネレータを初期化

        Args:
            font_path: 使用するフォントのパス（Noneの場合はデフォルトフォント）
        """
        self.font_path: Optional[str] = font_path
        if self.font_path is None:
            # 日本語対応フォントを自動検出
            self.font_path = self._find_japanese_font()

    @staticmethod
    def _find_japanese_font() -> Optional[str]:
        """
        システムから日本語フォントを検索

        Returns:
            日本語フォントのパス、見つからない場合はNone
        """
        # 優先順位付きで日本語フォントを検索
        preferred_fonts = [
            "Yu Gothic",
            "MS Gothic",
            "Meiryo",
            "IPAexGothic",
            "IPAGothic",
            "Hiragino Sans",
            "Noto Sans CJK JP",
        ]

        available_fonts = [f.name for f in fm.fontManager.ttflist]

        for font_name in preferred_fonts:
            if font_name in available_fonts:
                # フォント名からパスを取得
                for font in fm.fontManager.ttflist:
                    if font.name == font_name:
                        return font.fname

        # デフォルトとしてNoneを返す
        return None

    def generate_wordcloud(
        self,
        word_freq: Dict[str, int],
        width: int = 800,
        height: int = 400,
        background_color: str = "white",
        colormap: str = "viridis",
        max_words: int = 100,
    ) -> Image.Image:
        """
        単語の出現頻度からワードクラウド画像を生成

        Args:
            word_freq: 単語と出現回数の辞書
            width: 画像の幅（ピクセル）
            height: 画像の高さ（ピクセル）
            background_color: 背景色
            colormap: カラーマップ (matplotlib colormap name)
            max_words: 表示する最大単語数

        Returns:
            PIL Image オブジェクト
        """
        if not word_freq:
            # 単語がない場合は空白画像を返す
            return Image.new("RGB", (width, height), color=background_color)

        # WordCloudオブジェクトを作成
        wc_kwargs = {
            "width": width,
            "height": height,
            "background_color": background_color,
            "colormap": colormap,
            "max_words": max_words,
            "relative_scaling": 0.5,
            "min_font_size": 10,
        }

        # 日本語フォントが利用可能な場合は設定
        if self.font_path:
            wc_kwargs["font_path"] = self.font_path

        wordcloud = WordCloud(**wc_kwargs)

        # ワードクラウドを生成
        wordcloud.generate_from_frequencies(word_freq)

        # PIL Imageとして返す
        return wordcloud.to_image()

    def generate_wordcloud_figure(
        self,
        word_freq: Dict[str, int],
        width: int = 800,
        height: int = 400,
        background_color: str = "white",
        colormap: str = "viridis",
        max_words: int = 100,
        title: str = "ワードクラウド",
    ) -> plt.Figure:
        """
        ワードクラウドをmatplotlib Figureとして生成

        Args:
            word_freq: 単語と出現回数の辞書
            width: 画像の幅（ピクセル）
            height: 画像の高さ（ピクセル）
            background_color: 背景色
            colormap: カラーマップ
            max_words: 表示する最大単語数
            title: グラフタイトル

        Returns:
            matplotlib Figure オブジェクト
        """
        # ワードクラウド画像を生成
        image = self.generate_wordcloud(
            word_freq, width, height, background_color, colormap, max_words
        )

        # matplotlib Figureを作成
        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
        ax.imshow(image, interpolation="bilinear")
        ax.axis("off")
        ax.set_title(title, fontsize=16, pad=20)

        plt.tight_layout()

        return fig

    @staticmethod
    def get_available_colormaps() -> Dict[str, str]:
        """
        利用可能なカラーマップの一覧を取得

        Returns:
            カラーマップ名と説明の辞書
        """
        return {
            "viridis": "Viridis（紫〜黄緑）",
            "plasma": "Plasma（紫〜オレンジ）",
            "inferno": "Inferno（黒〜黄）",
            "magma": "Magma（黒〜白）",
            "cividis": "Cividis（青〜黄）",
            "twilight": "Twilight（青〜赤〜青）",
            "Blues": "Blues（白〜青）",
            "Reds": "Reds（白〜赤）",
            "Greens": "Greens（白〜緑）",
            "Purples": "Purples（白〜紫）",
            "Oranges": "Oranges（白〜オレンジ）",
            "RdYlBu": "RdYlBu（赤〜黄〜青）",
            "Spectral": "Spectral（赤〜黄〜青）",
            "coolwarm": "Coolwarm（青〜赤）",
        }
