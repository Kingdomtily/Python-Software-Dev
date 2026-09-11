from pathlib import Path

# Imported like any other installed third-party library -- nothing in
# this file reaches into weatherstats' internals or its source tree.
import weatherstats as ws

DATA_DIR = Path(__file__).parent / "data"
MIN_REQUIRED_RECORDS = 100_000


def load_dataset():
    """Load every CSV in data/, combining them if there's more than one."""
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {DATA_DIR}.\n"
            "Download a weather dataset from Kaggle "
            "(https://www.kaggle.com/datasets) and place the CSV(s) there."
        )
    if len(csv_files) == 1:
        return ws.load_weather_data(csv_files[0])
    return ws.load_and_combine_weather_data(csv_files)


def main() -> None:
    print(f"weatherstats version: {ws.__version__}\n")

    df = load_dataset()
    print(f"Loaded {len(df):,} total records.")
    if len(df) < MIN_REQUIRED_RECORDS:
        print(f"WARNING: below the {MIN_REQUIRED_RECORDS:,}-record minimum.\n")
    else:
        print(f"(Meets the {MIN_REQUIRED_RECORDS:,}-record minimum.)\n")

    stats_table = ws.descriptive_stats(df)
    print("Descriptive statistics (numeric columns):\n")
    print(stats_table.round(2))


if __name__ == "__main__":
    main()
