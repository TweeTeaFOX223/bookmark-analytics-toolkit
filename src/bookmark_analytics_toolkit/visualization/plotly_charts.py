"""Plotlyベースのインタラクティブチャート生成モジュール"""

from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
import polars as pl


class PlotlyCharts:
    """Plotlyインタラクティブチャート生成クラス"""

    @staticmethod
    def create_bar_chart(
        df: pl.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "棒グラフ",
        orientation: str = "v",
        show_values: bool = True,
        show_percentage: bool = False,
    ) -> go.Figure:
        """
        棒グラフを作成

        Args:
            df: データフレーム
            x_col: X軸のカラム名 (横向きの場合はY軸)
            y_col: Y軸のカラム名 (横向きの場合はX軸)
            title: グラフタイトル
            orientation: 向き ('v'=縦, 'h'=横)
            show_values: 値を表示するか
            show_percentage: パーセンテージを表示するか

        Returns:
            Plotly Figureオブジェクト
        """
        x_data: List[Any] = df[x_col].to_list()
        y_data: List[Any] = df[y_col].to_list()

        # パーセンテージ計算
        total: float = sum(y_data) if show_percentage else 0.0
        percentages: List[float] = [
            val / total * 100 if total > 0 else 0 for val in y_data
        ]

        # ホバーテキスト作成
        hover_template: str = "<b>%{customdata[0]}</b><br>"
        hover_template += f"件数: %{{customdata[1]:,}}<br>"
        if show_percentage:
            hover_template += "割合: %{customdata[2]:.1f}%"
        hover_template += "<extra></extra>"

        custom_data: List[List[Any]] = []
        for i in range(len(x_data)):
            row: List[Any] = [x_data[i], y_data[i]]
            if show_percentage:
                row.append(percentages[i])
            custom_data.append(row)

        if orientation == "h":
            # 横向き棒グラフ
            fig: go.Figure = go.Figure(
                go.Bar(
                    x=y_data,
                    y=x_data,
                    orientation="h",
                    marker=dict(color=y_data, colorscale="Viridis", showscale=False,),
                    text=[
                        f"{val:,}" + (f" ({pct:.1f}%)" if show_percentage else "")
                        for val, pct in zip(y_data, percentages)
                    ],
                    textposition="outside" if show_values else "none",
                    customdata=custom_data,
                    hovertemplate=hover_template,
                )
            )
            fig.update_xaxes(title=y_col)
            fig.update_yaxes(title=x_col)
        else:
            # 縦向き棒グラフ
            fig = go.Figure(
                go.Bar(
                    x=x_data,
                    y=y_data,
                    marker=dict(color=y_data, colorscale="Blues", showscale=False,),
                    text=[
                        f"{val:,}" + (f" ({pct:.1f}%)" if show_percentage else "")
                        for val, pct in zip(y_data, percentages)
                    ],
                    textposition="outside" if show_values else "none",
                    customdata=custom_data,
                    hovertemplate=hover_template,
                )
            )
            fig.update_xaxes(title=x_col)
            # 縦向きグラフの場合、上部余白を確保するためY軸範囲を調整
            if y_data and show_values:
                max_y = max(y_data)
                fig.update_yaxes(title=y_col, range=[0, max_y * 1.15])
            else:
                fig.update_yaxes(title=y_col)

        fig.update_layout(
            title=title, template="plotly_white", hovermode="closest", showlegend=False,
        )

        return fig

    @staticmethod
    def create_line_chart(
        df: pl.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "折れ線グラフ",
        show_markers: bool = True,
        show_values: bool = False,
    ) -> go.Figure:
        """
        折れ線グラフを作成

        Args:
            df: データフレーム
            x_col: X軸のカラム名
            y_col: Y軸のカラム名
            title: グラフタイトル
            show_markers: マーカーを表示するか
            show_values: 値を表示するか

        Returns:
            Plotly Figureオブジェクト
        """
        x_data: List[Any] = df[x_col].to_list()
        y_data: List[Any] = df[y_col].to_list()

        # ホバーテキスト
        hover_template: str = "<b>%{x}</b><br>件数: %{y:,}<extra></extra>"

        mode: str = "lines+markers" if show_markers else "lines"
        if show_values:
            mode = "lines+markers+text"

        fig: go.Figure = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y_data,
                mode=mode,
                name=y_col,
                line=dict(color="royalblue", width=2),
                marker=dict(size=6, color="royalblue"),
                text=[f"{val:,}" for val in y_data] if show_values else None,
                textposition="top center",
                hovertemplate=hover_template,
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode="x unified",
            template="plotly_white",
            showlegend=False,
        )

        return fig

    @staticmethod
    def create_pie_chart(
        df: pl.DataFrame, labels_col: str, values_col: str, title: str = "円グラフ",
    ) -> go.Figure:
        """
        円グラフを作成

        Args:
            df: データフレーム
            labels_col: ラベルのカラム名
            values_col: 値のカラム名
            title: グラフタイトル

        Returns:
            Plotly Figureオブジェクト
        """
        labels: List[Any] = df[labels_col].to_list()
        values: List[Any] = df[values_col].to_list()

        fig: go.Figure = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                textinfo="label+percent",
                marker=dict(line=dict(color="white", width=2)),
                hovertemplate="<b>%{label}</b><br>件数: %{value:,}<br>割合: %{percent}<extra></extra>",
            )
        )

        fig.update_layout(
            title=title, template="plotly_white",
        )

        return fig

    @staticmethod
    def create_heatmap(
        heatmap_data: Dict[str, Any], title: str = "ヒートマップ", colorscale: str = "YlOrRd",
    ) -> go.Figure:
        """
        ヒートマップを作成

        Args:
            heatmap_data: ヒートマップデータ (x_labels, y_labels, values含む辞書)
            title: グラフタイトル
            colorscale: カラースケール名

        Returns:
            Plotly Figureオブジェクト
        """
        fig: go.Figure = go.Figure(
            go.Heatmap(
                z=heatmap_data["values"],
                x=heatmap_data["x_labels"],
                y=heatmap_data["y_labels"],
                colorscale=colorscale,
                text=heatmap_data["values"],
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
                hovertemplate="<b>%{y}, %{x}</b><br>件数: %{z}<extra></extra>",
            )
        )

        fig.update_layout(
            title=title, xaxis_title="", yaxis_title="", template="plotly_white",
        )

        return fig

    @staticmethod
    def create_treemap(
        treemap_data: Dict[str, Any], title: str = "ツリーマップ", height: int = 600,
    ) -> go.Figure:
        """
        ツリーマップを作成

        Args:
            treemap_data: ツリーマップデータ (labels, parents, values, text含む辞書)
            title: グラフタイトル
            height: グラフの高さ

        Returns:
            Plotly Figureオブジェクト
        """
        fig: go.Figure = go.Figure(
            go.Treemap(
                labels=treemap_data["labels"],
                parents=treemap_data["parents"],
                values=treemap_data["values"],
                text=treemap_data.get("text", treemap_data["labels"]),
                textposition="middle center",
                marker=dict(colorscale="Blues", line=dict(width=2),),
                hovertemplate="<b>%{label}</b><br>%{text}<extra></extra>",
            )
        )

        fig.update_layout(
            title=title, margin=dict(t=50, l=25, r=25, b=25), height=height,
        )

        return fig

    @staticmethod
    def create_sunburst(
        sunburst_data: Dict[str, Any], title: str = "サンバーストチャート",
    ) -> go.Figure:
        """
        サンバーストチャートを作成

        Args:
            sunburst_data: サンバーストデータ (labels, parents, values含む辞書)
            title: グラフタイトル

        Returns:
            Plotly Figureオブジェクト
        """
        fig: go.Figure = go.Figure(
            go.Sunburst(
                labels=sunburst_data["labels"],
                parents=sunburst_data["parents"],
                values=sunburst_data["values"],
                branchvalues="total",
                marker=dict(colorscale="RdBu", line=dict(width=2)),
                hovertemplate="<b>%{label}</b><br>件数: %{value}<extra></extra>",
            )
        )

        fig.update_layout(
            title=title, margin=dict(t=50, l=0, r=0, b=0),
        )

        return fig
