"""
main.py -- Module 2, Phase 1 driver script.

This is the updated version of the Module 1 - Phase 1 script. Per the
assignment, it now:

  1. Uses pandas (via weatherstats) to read the Kaggle "Rain in
     Australia" weather dataset CSV(s) instead of whatever ad-hoc
     loading Module 1 used.
  2. Prints descriptive statistics (mean, median, mode, range, etc.).
  3. Gets all of that behavior from the `weatherstats` package -- a
     separately built, pip-installed package -- rather than from code
     copy-pasted into this file. That is the modularization this
     assignment is demonstrating: `weatherstats` is used here exactly
     the way you'd use pandas or numpy, via a plain `import`.

Run this only AFTER installing the package (see README.md):
    pip install -e .
    python main.py

Dataset layout: Kaggle publishes a few different shapes of this
dataset. This script accepts either:
  - a single data/weatherAUS.csv, or
  - a pre-split "data/Weather Training Data.csv" +
    "data/Weather Test Data.csv" pair (used so the combined row count
    clears the assignment's 100k-record minimum even when the training
    split alone falls just short of it).
"""

from pathlib import Path

# Imported like any other installed third-party library -- nothing in
# this file reaches into weatherstats' internals or its source tree.
import weatherstats as ws

DATA_DIR = Path(__file__).parent / "data"
SINGLE_FILE_PATH = DATA_DIR / "weatherAUS.csv"
SPLIT_FILE_PATHS = [
    DATA_DIR / "Weather Training Data.csv",
    DATA_DIR / "Weather Test Data.csv",
]

# The subset of numeric columns most worth summarizing. Feel free to
# pass columns=None to ws.generate_summary_report to summarize every
# numeric column instead.
NUMERIC_COLUMNS_OF_INTEREST = [
    "MinTemp",
    "MaxTemp",
    "Rainfall",
    "Evaporation",
    "Sunshine",
    "WindGustSpeed",
    "Humidity9am",
    "Humidity3pm",
    "Pressure9am",
    "Pressure3pm",
    "WindSpeed9am",
    "WindSpeed3pm",
    "Temp9am",
    "Temp3pm",
]

MIN_REQUIRED_RECORDS = 100_000


def load_dataset() -> "pd.DataFrame":  # noqa: F821 - typing hint only, no import needed
    """
    Figure out which dataset shape is present in data/ and load it.

    Prefers a single weatherAUS.csv if present; otherwise falls back to
    combining the pre-split training + test files.
    """
    if SINGLE_FILE_PATH.exists():
        return ws.load_weather_data(SINGLE_FILE_PATH)

    existing_split_files = [p for p in SPLIT_FILE_PATHS if p.exists()]
    if existing_split_files:
        return ws.load_and_combine_weather_data(existing_split_files)

    raise FileNotFoundError(
        "No weather dataset found in the data/ folder.\n"
        f"Expected either '{SINGLE_FILE_PATH.name}', or both "
        f"{[p.name for p in SPLIT_FILE_PATHS]}.\n"
        "Download a weather dataset from Kaggle (https://www.kaggle.com/datasets) "
        "and place the CSV(s) in data/. See README.md for details."
    )


def main() -> None:
    print(f"weatherstats version: {ws.__version__}\n")

    df = load_dataset()
    print(f"Loaded {len(df):,} total records.")
    if len(df) < MIN_REQUIRED_RECORDS:
        print(
            f"WARNING: this is below the assignment's "
            f"{MIN_REQUIRED_RECORDS:,}-record minimum.\n"
        )
    else:
        print(f"(Meets the {MIN_REQUIRED_RECORDS:,}-record minimum.)\n")

    # Only summarize columns that actually exist in this CSV (keeps the
    # script working across different dataset variants/column sets).
    available_columns = [c for c in NUMERIC_COLUMNS_OF_INTEREST if c in df.columns]

    report_text, stats_table = ws.generate_summary_report(
        df,
        columns=available_columns or None,
        title="Australian Weather Dataset - Descriptive Statistics",
    )
    print(report_text)

    # Also demonstrate the lower-level API for anyone grading who wants
    # to see the raw DataFrame return value, not just the printed text.
    print("\n--- Raw stats_table (pandas.DataFrame) ---")
    print(stats_table.round(2))


if __name__ == "__main__":
    main()
