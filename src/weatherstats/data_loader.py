from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

import pandas as pd

# Column names that, if present in a given CSV's header, get parsed as
# dates. Not every dataset has one of these (some are indexed by a
# plain row id instead), so a name is only ever parsed if it's actually
# present in that file's header -- never assumed.
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
            f"Could not find a weather dataset at '{csv_path}'. "
            "Download a weather dataset from Kaggle "
            "(https://www.kaggle.com/datasets) and place it at that "
            "path, or pass the correct path to load_weather_data()."
        )

    header = _read_header(csv_path)
    date_cols_present = [c for c in KNOWN_DATE_COLUMNS if c in header]
    if usecols is not None:
        date_cols_present = [c for c in date_cols_present if c in usecols]

    return pd.read_csv(
        csv_path,
        usecols=usecols,
        parse_dates=date_cols_present if date_cols_present else None,
    )


def load_and_combine_weather_data(
    csv_paths: Iterable[Union[str, Path]],
    add_source_column: bool = True,
) -> pd.DataFrame:
    """
    Load and concatenate several weather CSVs into one DataFrame.

    Useful for datasets pre-split across multiple files (e.g. a
    training file and a test file) where a single split may fall short
    of a minimum row-count requirement but the files together clear it.
    Columns present in some files but not others (for example a target
    column only present in the training split) are aligned
    automatically -- rows from a file missing that column get ``NaN``.

    Parameters
    ----------
    csv_paths : iterable of str or pathlib.Path
        Paths to the CSV files to combine, in order.
    add_source_column : bool
        If True (default), add a ``source_file`` column recording which
        input file each row came from.

    Returns
    -------
    pandas.DataFrame
        The concatenated data, with a fresh 0-based index.
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

    return pd.concat(frames, ignore_index=True, sort=False)


def numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of numeric (int/float) column names in ``df``."""
    return df.select_dtypes(include="number").columns.tolist()
