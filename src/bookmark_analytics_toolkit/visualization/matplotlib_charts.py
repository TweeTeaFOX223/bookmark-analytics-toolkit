"""Matplotlib-based static charts."""

import matplotlib.pyplot as plt
import matplotlib_fontja  # noqa
import polars as pl
from matplotlib.figure import Figure


class MatplotlibCharts:
    """Generator for Matplotlib static charts."""

    @staticmethod
    def create_line_chart(
        df: pl.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Time Series",
        figsize=(10, 6),
    ) -> Figure:
        """
        Create a line chart.

        Args:
            df: DataFrame with data
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            title: Chart title
            figsize: Figure size

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(
            df[x_col].to_list(),
            df[y_col].to_list(),
            marker="o",
            linewidth=2,
            markersize=4,
        )

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        return fig

    @staticmethod
    def create_bar_chart(
        df: pl.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Bar Chart",
        figsize=(10, 6),
        horizontal: bool = False,
    ) -> Figure:
        """
        Create a bar chart.

        Args:
            df: DataFrame with data
            x_col: Column name for categories
            y_col: Column name for values
            title: Chart title
            figsize: Figure size
            horizontal: If True, create horizontal bar chart

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        x_data = df[x_col].to_list()
        y_data = df[y_col].to_list()

        if horizontal:
            ax.barh(x_data, y_data, color="steelblue")
            ax.set_xlabel(y_col, fontsize=12)
            ax.set_ylabel(x_col, fontsize=12)
        else:
            ax.bar(x_data, y_data, color="steelblue")
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            plt.xticks(rotation=45, ha="right")

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="y" if not horizontal else "x")

        plt.tight_layout()

        return fig

    @staticmethod
    def create_histogram(
        df: pl.DataFrame,
        col: str,
        bins: int = 30,
        title: str = "Distribution",
        figsize=(10, 6),
    ) -> Figure:
        """
        Create a histogram.

        Args:
            df: DataFrame with data
            col: Column name to plot
            bins: Number of bins
            title: Chart title
            figsize: Figure size

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        data = df[col].to_list()
        ax.hist(data, bins=bins, color="skyblue", edgecolor="black", alpha=0.7)

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(col, fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()

        return fig

    @staticmethod
    def create_pie_chart(
        df: pl.DataFrame,
        labels_col: str,
        values_col: str,
        title: str = "Distribution",
        figsize=(8, 8),
    ) -> Figure:
        """
        Create a pie chart.

        Args:
            df: DataFrame with data
            labels_col: Column name for labels
            values_col: Column name for values
            title: Chart title
            figsize: Figure size

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        labels = df[labels_col].to_list()
        values = df[values_col].to_list()

        ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 10},
        )

        ax.set_title(title, fontsize=14, fontweight="bold")

        plt.tight_layout()

        return fig

    @staticmethod
    def create_cumulative_chart(
        df: pl.DataFrame,
        x_col: str,
        y_col: str,
        cumulative_col: str,
        title: str = "Cumulative Growth",
        figsize=(12, 6),
    ) -> Figure:
        """
        Create a chart with both daily and cumulative counts.

        Args:
            df: DataFrame with data
            x_col: Column name for x-axis
            y_col: Column name for daily counts
            cumulative_col: Column name for cumulative counts
            title: Chart title
            figsize: Figure size

        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

        x_data = df[x_col].to_list()
        y_data = df[y_col].to_list()
        cumulative_data = df[cumulative_col].to_list()

        # Daily counts
        ax1.bar(x_data, y_data, color="steelblue", alpha=0.7)
        ax1.set_ylabel("Daily Count", fontsize=12)
        ax1.set_title(f"{title} - Daily", fontsize=12, fontweight="bold")
        ax1.grid(True, alpha=0.3, axis="y")

        # Cumulative counts
        ax2.plot(
            x_data,
            cumulative_data,
            linewidth=2,
            color="darkblue",
            marker="o",
            markersize=3,
        )
        ax2.fill_between(x_data, cumulative_data, alpha=0.3, color="steelblue")
        ax2.set_xlabel(x_col, fontsize=12)
        ax2.set_ylabel("Cumulative Count", fontsize=12)
        ax2.set_title(f"{title} - Cumulative", fontsize=12, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        return fig
