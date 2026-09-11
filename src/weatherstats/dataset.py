"""
The storage class.

``WeatherDataset`` is where loaded data actually lives once it's been
fetched. In Phase 2 a bare ``pandas.DataFrame`` was passed directly
between functions; here it's wrapped in an object that:

- validates what it's given (encapsulation: the DataFrame itself is kept
  in a "private" ``_data`` attribute and only ever handed out through a
  read-only ``data`` property),
- exposes a small, purposeful API (``numeric_columns``, ``meets_minimum``)
  instead of letting every caller reach in and call arbitrary pandas
  methods, and
- supports Python's built-in conventions through dunder/magic methods
  (``__len__``, ``__repr__``, ``__str__``, ``__eq__``) so a
  ``WeatherDataset`` behaves the way experienced Python users expect
  (``len(dataset)``, ``print(dataset)``, ``dataset_a == dataset_b``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import pandas as pd

if TYPE_CHECKING:
    from .data_sources import DataSource


class WeatherDataset:
    """
    Wraps a pandas DataFrame of weather records.

    Parameters
    ----------
    data : pandas.DataFrame
        The already-fetched weather data.
    name : str
        A short human-readable label, mostly used in ``__repr__``/``__str__``.
    """

    def __init__(self, data: pd.DataFrame, name: str = "dataset") -> None:
        self._validate(data)
        self._data = data
        self._name = name

    # -- alternate constructor ------------------------------------------------
    @classmethod
    def from_data_source(cls, source: "DataSource", name: str = "dataset") -> "WeatherDataset":
        """Build a dataset directly from a ``DataSource`` by fetching it.

        A classmethod makes a natural second constructor here: the normal
        ``__init__`` takes data that's already in hand, while this one
        takes a fetcher and does the fetching for you.
        """
        return cls(source.fetch(), name=name)

    # -- validation -------------------------------------------------------------
    @staticmethod
    def _validate(data: pd.DataFrame) -> None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("WeatherDataset requires a pandas DataFrame.")
        if data.empty:
            raise ValueError("WeatherDataset cannot be created from an empty DataFrame.")

    # -- encapsulated access -----------------------------------------------------
    @property
    def data(self) -> pd.DataFrame:
        """Read-only access to the underlying DataFrame.

        There's no public setter: once a dataset is constructed, swapping
        out its data wholesale isn't something callers should be able to
        do, so that door is simply not offered.
        """
        return self._data

    @property
    def name(self) -> str:
        return self._name

    @property
    def numeric_columns(self) -> List[str]:
        """Names of the numeric (int/float) columns in this dataset."""
        return self._data.select_dtypes(include="number").columns.tolist()

    def meets_minimum(self, minimum: int) -> bool:
        """Whether this dataset has at least ``minimum`` records."""
        return len(self) >= minimum

    # -- dunder / magic methods ---------------------------------------------
    def __len__(self) -> int:
        """``len(dataset)`` returns the record count."""
        return len(self._data)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self._name!r}, records={len(self):,})"

    def __str__(self) -> str:
        return (
            f"'{self._name}' dataset: {len(self):,} records, "
            f"{len(self.numeric_columns)} numeric columns"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WeatherDataset):
            return NotImplemented
        return self._name == other._name and self._data.equals(other._data)
