from __future__ import annotations
from typing import Optional, Sequence
import pandas as pd

def descriptive_stats(
    df: pd.DataFrame,
    columns: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """
    Compute descriptive statistics for the numeric columns of ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
    columns : sequence of str, optional
        Restrict the computation to these columns. Defaults to every
        numeric column in ``df``.

    Returns
    -------
    pandas.DataFrame
        One row per statistic (count, mean, median, mode, std, min,
        max, range) and one column per numeric field.
    """
    numeric_df = df.select_dtypes(include="number")
    if columns is not None:
        missing = [c for c in columns if c not in numeric_df.columns]
        if missing:
            raise KeyError(f"Not numeric columns (or not found): {missing}")
        numeric_df = numeric_df[list(columns)]
    if numeric_df.empty:
        raise ValueError("No numeric columns available to summarize.")
    mode_row = numeric_df.mode().iloc[0]  # first mode if there are ties
    stats = {
        "count": numeric_df.count(),
        "mean": numeric_df.mean(),
        "median": numeric_df.median(),
        "mode": mode_row,
        "std": numeric_df.std(),
        "min": numeric_df.min(),
        "max": numeric_df.max(),
        "range": numeric_df.max() - numeric_df.min(),
    }
    return pd.DataFrame(stats).T

def value_counts_summary(df: pd.DataFrame, column: str, top_n: int = 5) -> pd.Series:
    """
    Convenience helper for categorical columns (e.g. ``Location`` or
    ``RainToday``): the ``top_n`` most frequent values and their counts.
    """
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")
    return df[column].value_counts().head(top_n)
