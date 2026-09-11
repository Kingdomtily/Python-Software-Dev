"""
The orchestrator.

``WeatherAnalysisApp`` doesn't fetch, store, or process data itself --
it *composes* objects that do: a ``DataSource`` to fetch with, a
``WeatherDataset`` to hold what comes back, and whatever ``StatsProcessor``
objects it's asked to run. This is composition (HAS-A) rather than
inheritance (IS-A): an app isn't a kind of data source or processor, it
just uses them together, which is exactly the relationship between these
classes.

Keeping this orchestration in its own class (rather than, say, writing it
straight into ``main.py``) is what lets ``main.py`` stay a thin script.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .data_sources import CombinedCsvDataSource, CsvFileDataSource, DataSource
from .dataset import WeatherDataset
from .processors import StatsProcessor


class WeatherAnalysisApp:
    """Ties a data source, a dataset, and one or more processors together."""

    #: Class variable: shared by every instance (a default, not per-app state).
    MIN_REQUIRED_RECORDS = 100_000

    def __init__(self, data_source: DataSource, name: str = "weather") -> None:
        self._data_source = data_source
        self._name = name
        self._dataset: Optional[WeatherDataset] = None

    @classmethod
    def from_directory(cls, data_dir: Union[str, Path]) -> "WeatherAnalysisApp":
        """
        Alternate constructor: build an app whose data source is "every
        CSV in this directory," combining them automatically if there's
        more than one.
        """
        data_dir = Path(data_dir)
        csv_files = sorted(data_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in {data_dir}.\n"
                "Download a weather dataset from Kaggle "
                "(https://www.kaggle.com/datasets) and place the CSV(s) there."
            )

        source: DataSource
        if len(csv_files) == 1:
            source = CsvFileDataSource(csv_files[0])
        else:
            source = CombinedCsvDataSource(csv_files)

        return cls(source)

    @property
    def dataset(self) -> WeatherDataset:
        """The loaded dataset. Raises if :meth:`load` hasn't run yet."""
        if self._dataset is None:
            raise RuntimeError("No dataset loaded yet -- call load() first.")
        return self._dataset

    def load(self) -> WeatherDataset:
        """Fetch from the data source and store the result as a WeatherDataset."""
        self._dataset = WeatherDataset.from_data_source(self._data_source, name=self._name)
        return self._dataset

    def run_processor(self, processor: StatsProcessor) -> object:
        """Run any ``StatsProcessor`` against the currently loaded dataset."""
        return processor.process(self.dataset)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(source={self._data_source!r})"
