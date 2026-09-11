"""
Data-processing classes.

Phase 2's ``stats.py`` had two free functions, ``descriptive_stats`` and
``value_counts_summary``. Here they become two classes that share a common
abstract base, ``StatsProcessor``, with a single ``process(dataset)``
method. Anything that can be handed a ``WeatherDataset`` and asked to
``process()`` it counts as a processor -- ``app.py`` doesn't need to know
which concrete kind it's holding, it just calls ``process()`` (polymorphism
again, same pattern as the data sources).

Splitting it this way also means adding a third kind of analysis later
(Phase 4+) is a matter of writing one more small class, not growing a
single do-everything function.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

import pandas as pd

from .dataset import WeatherDataset


class StatsProcessor(ABC):
    """Abstract base class for anything that turns a WeatherDataset into a result."""

    @abstractmethod
    def process(self, dataset: WeatherDataset) -> object:
        """Run this processor's analysis on ``dataset`` and return the result."""
        raise NotImplementedError


class DescriptiveStatsProcessor(StatsProcessor):
    """
    Computes descriptive statistics for a dataset's numeric columns.

    Parameters
    ----------
    columns : sequence of str, optional
        Restrict the computation to these columns. Defaults to every
        numeric column in the dataset. Stored on the instance so the same
        processor can be reused across multiple datasets with the same
        configuration.
    """

    def __init__(self, columns: Optional[Sequence[str]] = None) -> None:
        self._columns = columns

    def process(self, dataset: WeatherDataset) -> pd.DataFrame:
        """
        Returns
        -------
        pandas.DataFrame
            One row per statistic (count, mean, median, mode, std, min,
            max, range) and one column per numeric field.
        """
        numeric_df = dataset.data.select_dtypes(include="number")

        if self._columns is not None:
            missing = [c for c in self._columns if c not in numeric_df.columns]
            if missing:
                raise KeyError(f"Not numeric columns (or not found): {missing}")
            numeric_df = numeric_df[list(self._columns)]

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

    def __repr__(self) -> str:
        return f"{type(self).__name__}(columns={self._columns!r})"


class ValueCountsProcessor(StatsProcessor):
    """
    Convenience processor for categorical columns (e.g. ``Location`` or
    ``RainToday``): the ``top_n`` most frequent values and their counts.
    """

    def __init__(self, column: str, top_n: int = 5) -> None:
        self._column = column
        self._top_n = top_n

    def process(self, dataset: WeatherDataset) -> pd.Series:
        df = dataset.data
        if self._column not in df.columns:
            raise KeyError(f"Column '{self._column}' not found in DataFrame.")
        return df[self._column].value_counts().head(self._top_n)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(column={self._column!r}, top_n={self._top_n!r})"
