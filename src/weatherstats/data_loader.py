"""
data_loader.py
---------------

Responsible for exactly one thing: getting raw weather data from CSV
file(s) on disk into a pandas DataFrame. Keeping this separate from the
statistics logic (see :mod:`weatherstats.stats`) is part of the
modularization goal for this assignment -- loading concerns and
analysis concerns are decoupled, so either one can change or be reused
independently.

Kaggle publishes several variants of the "Rain in Australia" weather
dataset. Some ship as a single ``weatherAUS.csv`` with a ``Date``
column; others (e.g. the "Weather Dataset - Rattle Package" mirrors
used in several intro-to-ML courses) ship as a pre-split
``Weather Training Data.csv`` / ``Weather Test Data.csv`` pair, indexed
by a ``row ID`` column instead of a date, with no ``RainTomorrow``
column in the test half (it's the prediction target). This module
handles both shapes without hardcoding either one's column list.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

import pandas as pd

# Any of these column names, if present in a given CSV's header, will be
# parsed as dates. Declared once so callers don't repeat string
# literals. Not every dataset variant has one of these (e.g. datasets
# indexed by "row ID" instead), so we only ever parse a name that is
# actually present in that file's header -- never assume it blindly.
KNOWN_DATE_COLUMNS = ["Date", "date"]


def _read_header(csv_path: Path) -> List[str]:
    """Return just the column names of a CSV, without loading any rows."""
    return list(pd.read_csv(csv_path, nrows=0).columns)


def load_weather_data(
    csv_path: Union[str, Path],
    usecols: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """
    Load a single weather-dataset CSV into a pandas DataFrame.

    Works with any of the common Kaggle "Rain in Australia" variants:
    a ``weatherAUS.csv`` with a ``Date`` column, or a
    ``Weather Training/Test Data.csv`` file indexed by ``row ID``. Any
    recognized date column that is actually present is parsed as a
    real datetime; everything else is left as pandas infers it.

    Parameters
    ----------
    csv_path : str or pathlib.Path
        Path to the weather CSV file.
    usecols : sequence of str, optional
        If given, only load these columns (passed straight through to
        ``pandas.read_csv``).

    Returns
    -------
    pandas.DataFrame

    Raises
    ------
    FileNotFoundError
        If ``csv_path`` does not exist.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find a weather dataset at '{csv_path}'.\n"
            "Download a weather dataset from Kaggle "
            "(https://www.kaggle.com/datasets) and place it at that "
            "path, or pass the correct path to load_weather_data()."
        )

    header = _read_header(csv_path)
    date_cols_present = [c for c in KNOWN_DATE_COLUMNS if c in header]
    if usecols is not None:
        date_cols_present = [c for c in date_cols_present if c in usecols]

    df = pd.read_csv(
        csv_path,
        usecols=usecols,
        parse_dates=date_cols_present if date_cols_present else None,
    )
    return df


def load_and_combine_weather_data(
    csv_paths: Iterable[Union[str, Path]],
    add_source_column: bool = True,
) -> pd.DataFrame:
    """
    Load and concatenate several weather CSVs into one DataFrame.

    This is for dataset variants that ship pre-split across multiple
    files (e.g. ``Weather Training Data.csv`` + ``Weather Test Data.csv``)
    -- useful when a single split falls short of a minimum row-count
    requirement but the files together clear it. Columns that exist in
    some files but not others (for example a ``RainTomorrow`` target
    column present only in a training split) are aligned automatically;
    rows from files missing a column simply get ``NaN`` there.

    Parameters
    ----------
    csv_paths : iterable of str or pathlib.Path
        Paths to the CSV files to combine, in order.
    add_source_column : bool
        If True (default), add a ``source_file`` column recording which
        input file each row came from -- useful since some pre-split
        datasets reuse the same row-id values (e.g. "Row0") across
        their train and test files.

    Returns
    -------
    pandas.DataFrame
        The concatenated data, with a fresh 0-based index.

    Raises
    ------
    FileNotFoundError
        If any path in ``csv_paths`` does not exist.
    ValueError
        If ``csv_paths`` is empty.
    """
    paths = [Path(p) for p in csv_paths]
    if not paths:
        raise ValueError("csv_paths must contain at least one file.")

    frames = []
    for path in paths:
        frame = load_weather_data(path)
        if add_source_column:
            frame = frame.copy()
            frame["source_file"] = path.name
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True, sort=False)
    return combined


def numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of numeric (int/float) column names in ``df``."""
    return df.select_dtypes(include="number").columns.tolist()
