from pathlib import Path

# Imported like any other installed third-party library -- nothing in
# this file reaches into weatherstats' internals or its source tree.
import weatherstats as ws

DATA_DIR = Path(__file__).parent / "data"


def main() -> None:
    print(f"weatherstats version: {ws.__version__}\n")

    app = ws.WeatherAnalysisApp.from_directory(DATA_DIR)
    dataset = app.load()

    print(dataset)  # uses WeatherDataset.__str__
    if dataset.meets_minimum(ws.WeatherAnalysisApp.MIN_REQUIRED_RECORDS):
        print(f"(Meets the {ws.WeatherAnalysisApp.MIN_REQUIRED_RECORDS:,}-record minimum.)\n")
    else:
        print(f"WARNING: below the {ws.WeatherAnalysisApp.MIN_REQUIRED_RECORDS:,}-record minimum.\n")

    stats_table = app.run_processor(ws.DescriptiveStatsProcessor())
    print("Descriptive statistics (numeric columns):\n")
    print(stats_table.round(2))


if __name__ == "__main__":
    main()
