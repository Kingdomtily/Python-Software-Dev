"""
Data-fetching classes.

Phase 2 had a couple of free functions in ``data_loader.py`` that knew how
to turn a CSV path (or several) into a DataFrame. Phase 3 turns that same
behavior into a small class hierarchy so the "how do I get the raw data"
concern lives in its own objects instead of standalone functions:

``DataSource``
    An abstract base class (via the ``abc`` module) that defines the
    *interface* every data source must honor: a no-argument ``fetch()``
    that returns a ``pandas.DataFrame``. It can't be instantiated directly.

``CsvFileDataSource``
    Fetches data from a single CSV file on disk.

``CombinedCsvDataSource``
    Fetches data from several CSV files and concatenates them. It does
    this by *composing* several ``CsvFileDataSource`` objects internally
    rather than re-implementing file reading itself.

Because both concrete classes implement the same ``fetch()`` method,
anything that holds a ``DataSource`` (see ``app.py``) can call
``source.fetch()`` without caring which kind it actually has -- that's
polymorphism doing the work.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

import pandas as pd

# Column names that, if present in a given CSV's header, get parsed as
# dates. Not every dataset has one of these (some are indexed by a plain
# row id instead), so a name is only ever parsed if it's actually present
# in that file's header -- never assumed.
KNOWN_DATE_COLUMNS = ["Date", "date"]


class DataSource(ABC):
    """
    Abstract base class for anything that can fetch weather data.

    Subclasses must implement :meth:`fetch`. This class also bundles a
    couple of small CSV-header helpers shared by every CSV-backed
    subclass, so they don't each reimplement them.
    """

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Return the source's data as a pandas DataFrame."""
        raise NotImplementedError

    @staticmethod
    def _read_header(csv_path: Path) -> List[str]:
        """Return just a CSV's column names, without loading any rows."""
        return list(pd.read_csv(csv_path, nrows=0).columns)

    @classmethod
    def _date_columns_present(
        cls, header: Sequence[str], usecols: Optional[Sequence[str]] = None
    ) -> List[str]:
        """Of the columns we know how to parse as dates, which ones are
        actually in this file's header (and, if ``usecols`` was given,
        also among the columns being kept)?"""
        cols = [c for c in KNOWN_DATE_COLUMNS if c in header]
        if usecols is not None:
            cols = [c for c in cols if c in usecols]
        return cols


class CsvFileDataSource(DataSource):
    """Fetches weather data from a single CSV file."""

    def __init__(
        self,
        csv_path: Union[str, Path],
        usecols: Optional[Sequence[str]] = None,
    ) -> None:
        self._csv_path = Path(csv_path)
        self._usecols = usecols

    @property
    def csv_path(self) -> Path:
        """The file this data source reads from (read-only)."""
        return self._csv_path

    def fetch(self) -> pd.DataFrame:
        if not self._csv_path.exists():
            raise FileNotFoundError(
                f"Could not find a weather dataset at '{self._csv_path}'. "
                "Download a weather dataset from Kaggle "
                "(https://www.kaggle.com/datasets) and place it at that "
                "path, or point CsvFileDataSource at the correct path."
            )

        header = self._read_header(self._csv_path)
        date_cols = self._date_columns_present(header, self._usecols)

        return pd.read_csv(
            self._csv_path,
            usecols=self._usecols,
            parse_dates=date_cols if date_cols else None,
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self._csv_path)!r})"


class CombinedCsvDataSource(DataSource):
    """
    Fetches and combines weather data from multiple CSV files.

    Useful for datasets pre-split across multiple files (e.g. a training
    file and a test file) where a single split may fall short of a
    minimum row-count requirement but the files together clear it.
    Columns present in some files but not others (for example a target
    column only present in the training split) are aligned automatically
    -- rows from a file missing that column get ``NaN``.

    Internally this class *composes* a list of ``CsvFileDataSource``
    objects -- one per file -- and delegates the actual file reading to
    them rather than duplicating that logic.
    """

    def __init__(
        self,
        csv_paths: Iterable[Union[str, Path]],
        add_source_column: bool = True,
    ) -> None:
        paths = [Path(p) for p in csv_paths]
        if not paths:
            raise ValueError("csv_paths must contain at least one file.")
        self._sources = [CsvFileDataSource(p) for p in paths]
        self._add_source_column = add_source_column

    @property
    def file_names(self) -> List[str]:
        return [source.csv_path.name for source in self._sources]

    def fetch(self) -> pd.DataFrame:
        frames = []
        for source in self._sources:
            frame = source.fetch()
            if self._add_source_column:
                frame = frame.copy()
                frame["source_file"] = source.csv_path.name
            frames.append(frame)

        return pd.concat(frames, ignore_index=True, sort=False)

    def __len__(self) -> int:
        """Number of files this source will combine."""
        return len(self._sources)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.file_names!r})"
