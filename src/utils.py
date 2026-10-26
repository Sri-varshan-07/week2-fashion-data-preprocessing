"""
utils.py
--------
General-purpose helper utilities for the fashion data pipeline.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary DataFrame of missing values per column."""
    total = df.isnull().sum()
    percent = (total / len(df) * 100).round(2)
    report = pd.DataFrame({
        "missing_count": total,
        "missing_percent": percent,
        "dtype": df.dtypes,
    })
    return report[report["missing_count"] > 0].sort_values("missing_percent", ascending=False)


def plot_missing_heatmap(df: pd.DataFrame, save_path: str | Path | None = None) -> None:
    """Plot a heatmap of missing values."""
    try:
        import missingno as msno
        fig, ax = plt.subplots(figsize=(12, 6))
        msno.matrix(df, ax=ax, sparkline=False)
        plt.title("Missing Value Matrix", fontsize=14)
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            logger.info(f"Missing value heatmap saved to {save_path}")
        plt.show()
    except ImportError:
        logger.warning("missingno not installed. Run: pip install missingno")


def plot_distribution(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    save_path: str | Path | None = None,
) -> None:
    """Plot distributions for numeric columns."""
    num_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    n = len(num_cols)
    if n == 0:
        return

    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
    axes = np.array(axes).flatten()

    for i, col in enumerate(num_cols):
        sns.histplot(df[col].dropna(), kde=True, ax=axes[i], color="steelblue")
        axes[i].set_title(f"Distribution: {col}", fontsize=11)
        axes[i].set_xlabel(col)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info(f"Distribution plot saved to {save_path}")
    plt.show()


def summarize_dataframe(df: pd.DataFrame) -> None:
    """Print a comprehensive summary of a DataFrame."""
    print(f"\n{'='*60}")
    print(f"  DataFrame Summary")
    print(f"{'='*60}")
    print(f"  Shape         : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  Memory Usage  : {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"  Duplicate Rows: {df.duplicated().sum():,}")
    print(f"  Total Missing : {df.isnull().sum().sum():,}")
    print(f"\n  Column Types:")
    for dtype, count in df.dtypes.value_counts().items():
        print(f"    {str(dtype):<15} → {count} columns")
    print(f"{'='*60}\n")
    print(df.describe(include="all").T.to_string())
    print(f"\n{'='*60}\n")
