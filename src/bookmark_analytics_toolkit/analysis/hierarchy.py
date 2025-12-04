"""ブックマークフォルダ階層構造の分析モジュール"""

from typing import Dict, List, Any, Optional, Tuple
import polars as pl


class HierarchyAnalyzer:
    """ブックマークフォルダ階層分析クラス"""

    @staticmethod
    def build_treemap_data(
        df: pl.DataFrame, max_depth: Optional[int] = None, hierarchical: bool = True,
    ) -> Dict[str, Any]:
        """
        Plotlyツリーマップ用のデータ構造を構築

        Args:
            df: 前処理済みデータフレーム
            max_depth: 表示する最大階層深さ (Noneで全て)
            hierarchical: True=階層構造、False=グループ別

        Returns:
            ツリーマップデータの辞書 (labels, parents, values, text含む)
        """
        # 最大深さでフィルタ
        if max_depth:
            df = df.filter(pl.col("hierarchy_level") <= max_depth)

        if hierarchical:
            return HierarchyAnalyzer._build_hierarchical_treemap(df)
        else:
            return HierarchyAnalyzer._build_grouped_treemap(df)

    @staticmethod
    def _build_hierarchical_treemap(df: pl.DataFrame) -> Dict[str, Any]:
        """階層構造を考慮したツリーマップデータを構築"""
        # フォルダパスごとのブックマーク数をカウント
        folder_counts: pl.DataFrame = (
            df.group_by("Folder Path")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
        )

        labels: List[str] = []
        parents: List[str] = []
        values: List[int] = []
        text_labels: List[str] = []

        # ルートを追加
        labels.append("All Bookmarks")
        parents.append("")
        values.append(0)  # Plotlyが自動計算
        text_labels.append(f"{len(df)} URLs")

        # フォルダパスを処理
        seen_folders: set[str] = set()
        folder_stats: Dict[str, Dict[str, int]] = {}

        # まず全てのパスを収集して、子フォルダ数を事前に計算
        all_paths: List[str] = [
            row["Folder Path"] for row in folder_counts.iter_rows(named=True)
        ]

        # 各パスの子フォルダ数を計算
        path_children: Dict[str, int] = {}
        for path in all_paths:
            # パス区切り文字を統一（\または\\）
            normalized_path = path.replace("\\\\", "\\")
            parts = normalized_path.split("\\")

            # 各中間パスについても子フォルダ数をカウント
            for i in range(len(parts)):
                current = "\\".join(parts[: i + 1])
                if current not in path_children:
                    path_children[current] = 0

                # このパスの直接の子をカウント
                for other_path in all_paths:
                    other_normalized = other_path.replace("\\\\", "\\")
                    other_parts = other_normalized.split("\\")

                    # 直接の子かチェック（1階層だけ深い）
                    if len(other_parts) == len(
                        parts
                    ) + 1 and other_normalized.startswith(current + "\\"):
                        path_children[current] += 1

        # フォルダごとのURL数と子フォルダ数を計算
        for row in folder_counts.iter_rows(named=True):
            folder_path: str = row["Folder Path"]
            count: int = row["count"]

            # パス区切り文字を統一
            normalized_path = folder_path.replace("\\\\", "\\")
            parts: List[str] = normalized_path.split("\\")

            # 各階層のフォルダを処理
            for i in range(len(parts)):
                current_path: str = "\\".join(parts[: i + 1])

                if current_path not in seen_folders:
                    seen_folders.add(current_path)

                    # 現在のフォルダ名
                    folder_name: str = parts[i]

                    # 親パス
                    parent_path: str
                    if i == 0:
                        parent_path = "All Bookmarks"
                    else:
                        parent_path = "\\".join(parts[:i])

                    # このフォルダの直接のURL数（最終パスの場合のみ）
                    direct_url_count: int = 0
                    if current_path == normalized_path:
                        direct_url_count = count

                    # 子フォルダ数を取得
                    child_count: int = path_children.get(current_path, 0)

                    labels.append(current_path)
                    parents.append(parent_path)
                    values.append(
                        direct_url_count if direct_url_count > 0 else 1
                    )  # 最小値1で表示確保

                    # テキストラベル: フォルダ名、URL数、子フォルダ数
                    text_label: str = f"{folder_name}<br>"
                    text_label += f"URL数: {direct_url_count}<br>"
                    text_label += f"子フォルダ: {child_count}"
                    text_labels.append(text_label)

                    # 統計情報を保存
                    folder_stats[current_path] = {
                        "url_count": direct_url_count,
                        "child_count": child_count,
                    }

        return {
            "labels": labels,
            "parents": parents,
            "values": values,
            "text": text_labels,
        }

    @staticmethod
    def _build_grouped_treemap(df: pl.DataFrame) -> Dict[str, Any]:
        """各フォルダを別グループとして扱うツリーマップデータを構築"""
        # フォルダ名ごとのカウント
        folder_counts: pl.DataFrame = (
            df.group_by("Folder Name")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
        )

        labels: List[str] = ["All Bookmarks"]
        parents: List[str] = [""]
        values: List[int] = [0]
        text_labels: List[str] = [f"{len(df)} URLs"]

        for row in folder_counts.iter_rows(named=True):
            folder_name: str = row["Folder Name"]
            count: int = row["count"]

            labels.append(folder_name)
            parents.append("All Bookmarks")
            values.append(count)
            text_labels.append(f"{folder_name}<br>URL数: {count}")

        return {
            "labels": labels,
            "parents": parents,
            "values": values,
            "text": text_labels,
        }

    @staticmethod
    def build_sunburst_data(
        df: pl.DataFrame, max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Plotlyサンバーストチャート用のデータ構造を構築

        Args:
            df: 前処理済みデータフレーム
            max_depth: 表示する最大階層深さ

        Returns:
            サンバーストデータの辞書
        """
        # サンバーストはツリーマップと同じデータ構造を使用
        return HierarchyAnalyzer.build_treemap_data(df, max_depth, hierarchical=True)

    @staticmethod
    def get_folder_statistics(df: pl.DataFrame) -> pl.DataFrame:
        """
        各フォルダの統計情報を取得

        Args:
            df: 前処理済みデータフレーム

        Returns:
            フォルダ統計のデータフレーム
        """
        folder_stats: pl.DataFrame = (
            df.group_by("Folder Path")
            .agg(
                [
                    pl.count().alias("bookmark_count"),
                    pl.col("hierarchy_level").first().alias("depth"),
                    pl.col("created_datetime").min().alias("first_bookmark"),
                    pl.col("created_datetime").max().alias("last_bookmark"),
                ]
            )
            .sort("bookmark_count", descending=True)
        )

        return folder_stats

    @staticmethod
    def get_folder_timeline_heatmap(
        df: pl.DataFrame, top_n: int = 20,
    ) -> Dict[str, Any]:
        """
        フォルダ作成タイムラインのヒートマップデータを取得

        Args:
            df: 前処理済みデータフレーム
            top_n: 上位N個のフォルダを含める

        Returns:
            ヒートマップデータの辞書
        """
        # ブックマーク数でトップフォルダを取得
        top_folders: pl.DataFrame = (
            df.group_by("Folder Name")
            .agg(pl.count().alias("count"))
            .sort("count", descending=True)
            .head(top_n)
        )

        top_folder_names: List[str] = top_folders["Folder Name"].to_list()

        # トップフォルダのデータでフィルタ
        filtered_df: pl.DataFrame = df.filter(
            pl.col("Folder Name").is_in(top_folder_names)
        )

        # フォルダと年月でグループ化
        heatmap_data: pl.DataFrame = (
            filtered_df.group_by(["Folder Name", "created_year", "created_month"])
            .agg(pl.count().alias("count"))
            .sort(["Folder Name", "created_year", "created_month"])
        )

        # ユニークな年月の組み合わせを取得
        year_months: pl.DataFrame = (
            filtered_df.select(["created_year", "created_month"])
            .unique()
            .sort(["created_year", "created_month"])
        )

        # ラベルを作成
        x_labels: List[str] = [
            f"{row['created_year']}-{row['created_month']:02d}"
            for row in year_months.iter_rows(named=True)
        ]
        y_labels: List[str] = top_folder_names

        # 2次元配列を作成
        values: List[List[int]] = [
            [0 for _ in range(len(x_labels))] for _ in range(len(y_labels))
        ]

        for row in heatmap_data.iter_rows(named=True):
            folder_idx: int = y_labels.index(row["Folder Name"])
            year_month_label: str = f"{row['created_year']}-{row['created_month']:02d}"
            time_idx: int = x_labels.index(year_month_label)
            values[folder_idx][time_idx] = row["count"]

        return {
            "x_labels": x_labels,
            "y_labels": y_labels,
            "values": values,
        }

    @staticmethod
    def get_hierarchy_tree_structure(df: pl.DataFrame) -> Dict[str, Any]:
        """
        階層ツリー構造を取得 (ディレクトリツリー表示用)

        Args:
            df: 前処理済みデータフレーム

        Returns:
            ネストされた辞書形式のツリー構造
        """
        tree: Dict[str, Any] = {
            "name": "Root",
            "children": [],
            "url_count": 0,
            "subfolder_count": 0,
        }

        # フォルダパスでグループ化
        folder_groups: pl.DataFrame = df.group_by("Folder Path").agg(
            pl.count().alias("count")
        )

        # パスの情報を保存（パス区切り文字を統一）
        path_info: Dict[str, Dict[str, int]] = {}
        all_paths: List[str] = []

        for row in folder_groups.iter_rows(named=True):
            folder_path: str = row["Folder Path"]
            count: int = row["count"]
            # パス区切り文字を統一
            normalized_path = folder_path.replace("\\\\", "\\")
            all_paths.append(normalized_path)
            path_info[normalized_path] = {"url_count": count, "subfolder_count": 0}

        # 子フォルダ数を計算
        for path in all_paths:
            child_count: int = sum(
                1
                for other_path in all_paths
                if other_path.startswith(path + "\\")
                and other_path.count("\\") == path.count("\\") + 1
            )
            path_info[path]["subfolder_count"] = child_count

        # ツリーを再帰的に構築
        for row in folder_groups.iter_rows(named=True):
            # パス区切り文字を統一
            normalized_path = row["Folder Path"].replace("\\\\", "\\")
            path_parts: List[str] = normalized_path.split("\\")

            # ツリーをナビゲート/作成
            current: Dict[str, Any] = tree
            current_path_parts: List[str] = []

            for part in path_parts:
                current_path_parts.append(part)
                full_current_path = "\\".join(current_path_parts)

                # 子要素を検索または作成
                child: Optional[Dict[str, Any]] = None
                for c in current.get("children", []):
                    if c["name"] == part:
                        child = c
                        break

                if child is None:
                    child = {
                        "name": part,
                        "children": [],
                        "url_count": 0,
                        "subfolder_count": 0,
                    }
                    if "children" not in current:
                        current["children"] = []
                    current["children"].append(child)

                current = child

            # リーフノードにカウントを追加
            if normalized_path in path_info:
                current["url_count"] = path_info[normalized_path]["url_count"]
                current["subfolder_count"] = path_info[normalized_path][
                    "subfolder_count"
                ]

        return tree

    @staticmethod
    def format_tree_text(tree: Dict[str, Any], indent: int = 0) -> str:
        """
        ツリー構造をテキスト形式でフォーマット

        Args:
            tree: ツリー構造の辞書
            indent: インデントレベル

        Returns:
            フォーマットされたツリーテキスト
        """
        lines: List[str] = []
        prefix: str = "  " * indent

        # ルート以外の場合、名前と統計情報を表示
        if indent > 0:
            name: str = tree["name"]
            url_count: int = tree.get("url_count", 0)
            subfolder_count: int = tree.get("subfolder_count", 0)
            line: str = f"{prefix}├─ {name} (URL数: {url_count}, 子フォルダ: {subfolder_count})"
            lines.append(line)

        # 子要素を再帰的に処理
        children: List[Dict[str, Any]] = tree.get("children", [])
        for child in children:
            lines.extend(
                HierarchyAnalyzer.format_tree_text(child, indent + 1).split("\n")
            )

        return "\n".join(lines)
