"""
Basic unit tests for the weatherstats package. Run with:

    pytest

These use small in-memory DataFrames (not the real Kaggle CSV) so they
run instantly and don't depend on the dataset being downloaded.
"""
import pandas as pd
import pytest

from weatherstats.stats import descriptive_stats, value_counts_summary
from weatherstats.report import generate_summary_report
from weatherstats.data_loader import load_weather_data, load_and_combine_weather_data


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "MinTemp": [10.0, 12.0, 12.0, 15.0, 8.0],
        "MaxTemp": [20.0, 22.0, 21.0, 25.0, 18.0],
        "RainToday": ["No", "Yes", "No", "No", "Yes"],
    })


def test_descriptive_stats_shape(sample_df):
    result = descriptive_stats(sample_df)
    assert set(result.index) == {
        "count", "mean", "median", "mode", "std", "min", "max", "range",
    }
    assert list(result.columns) == ["MinTemp", "MaxTemp"]


def test_descriptive_stats_values(sample_df):
    result = descriptive_stats(sample_df, columns=["MinTemp"])
    assert result.loc["min", "MinTemp"] == 8.0
    assert result.loc["max", "MinTemp"] == 15.0
    assert result.loc["range", "MinTemp"] == 7.0
    assert result.loc["mode", "MinTemp"] == 12.0
    assert result.loc["count", "MinTemp"] == 5


def test_descriptive_stats_rejects_non_numeric_column(sample_df):
    with pytest.raises(KeyError):
        descriptive_stats(sample_df, columns=["RainToday"])


def test_descriptive_stats_rejects_empty_numeric(sample_df):
    with pytest.raises(ValueError):
        descriptive_stats(sample_df[["RainToday"]])


def test_value_counts_summary(sample_df):
    counts = value_counts_summary(sample_df, "RainToday")
    assert counts["No"] == 3
    assert counts["Yes"] == 2


def test_generate_summary_report(sample_df):
    text, table = generate_summary_report(sample_df, title="Test Report")
    assert "Test Report" in text
    assert "Records analyzed: 5" in text
    assert table.shape[1] == 2


def test_load_weather_data_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_weather_data(tmp_path / "does_not_exist.csv")


def test_load_weather_data_without_date_column(tmp_path):
    # Mirrors the "row ID"-indexed Kaggle variant, which has no Date column.
    csv_path = tmp_path / "no_date.csv"
    pd.DataFrame({
        "row ID": ["Row0", "Row1"],
        "MinTemp": [10.0, 11.0],
        "RainToday": ["No", "Yes"],
    }).to_csv(csv_path, index=False)

    df = load_weather_data(csv_path)
    assert len(df) == 2
    assert "Date" not in df.columns


def test_load_and_combine_weather_data(tmp_path):
    train_path = tmp_path / "Weather Training Data.csv"
    test_path = tmp_path / "Weather Test Data.csv"

    pd.DataFrame({
        "row ID": ["Row0", "Row1"],
        "MinTemp": [10.0, 11.0],
        "RainTomorrow": [0, 1],
    }).to_csv(train_path, index=False)

    pd.DataFrame({
        "row ID": ["Row0", "Row1", "Row2"],
        "MinTemp": [9.0, 12.0, 13.0],
        # no RainTomorrow column here, like the real test split
    }).to_csv(test_path, index=False)

    combined = load_and_combine_weather_data([train_path, test_path])

    assert len(combined) == 5  # 2 + 3 rows combined
    assert "RainTomorrow" in combined.columns
    assert combined["RainTomorrow"].isna().sum() == 3  # test rows have no value
    assert set(combined["source_file"]) == {
        "Weather Training Data.csv",
        "Weather Test Data.csv",
    }


def test_load_and_combine_weather_data_requires_at_least_one_path():
    with pytest.raises(ValueError):
        load_and_combine_weather_data([])
