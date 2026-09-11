import pandas as pd
import pytest

from weatherstats.data_sources import CsvFileDataSource, CombinedCsvDataSource, DataSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import DescriptiveStatsProcessor, ValueCountsProcessor
from weatherstats.app import WeatherAnalysisApp


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "MinTemp": [10.0, 12.0, 12.0, 15.0, 8.0],
        "MaxTemp": [20.0, 22.0, 21.0, 25.0, 18.0],
        "RainToday": ["No", "Yes", "No", "No", "Yes"],
    })


@pytest.fixture
def sample_dataset(sample_df):
    return WeatherDataset(sample_df, name="sample")


# -- WeatherDataset (storage) -------------------------------------------------

def test_weather_dataset_len_and_str(sample_dataset):
    assert len(sample_dataset) == 5
    assert "sample" in str(sample_dataset)
    assert "5" in str(sample_dataset)


def test_weather_dataset_numeric_columns(sample_dataset):
    assert sample_dataset.numeric_columns == ["MinTemp", "MaxTemp"]


def test_weather_dataset_meets_minimum(sample_dataset):
    assert sample_dataset.meets_minimum(5) is True
    assert sample_dataset.meets_minimum(6) is False


def test_weather_dataset_equality(sample_df):
    a = WeatherDataset(sample_df, name="x")
    b = WeatherDataset(sample_df.copy(), name="x")
    c = WeatherDataset(sample_df.copy(), name="different")
    assert a == b
    assert a != c
    assert a != "not a dataset"


def test_weather_dataset_rejects_non_dataframe():
    with pytest.raises(TypeError):
        WeatherDataset([1, 2, 3])


def test_weather_dataset_rejects_empty_dataframe():
    with pytest.raises(ValueError):
        WeatherDataset(pd.DataFrame())


# -- DescriptiveStatsProcessor / ValueCountsProcessor (processing) -----------

def test_descriptive_stats_processor_shape(sample_dataset):
    result = DescriptiveStatsProcessor().process(sample_dataset)
    assert set(result.index) == {
        "count", "mean", "median", "mode", "std", "min", "max", "range",
    }
    assert list(result.columns) == ["MinTemp", "MaxTemp"]


def test_descriptive_stats_processor_values(sample_dataset):
    result = DescriptiveStatsProcessor(columns=["MinTemp"]).process(sample_dataset)
    assert result.loc["min", "MinTemp"] == 8.0
    assert result.loc["max", "MinTemp"] == 15.0
    assert result.loc["range", "MinTemp"] == 7.0
    assert result.loc["mode", "MinTemp"] == 12.0
    assert result.loc["count", "MinTemp"] == 5


def test_descriptive_stats_processor_rejects_non_numeric_column(sample_dataset):
    with pytest.raises(KeyError):
        DescriptiveStatsProcessor(columns=["RainToday"]).process(sample_dataset)


def test_value_counts_processor(sample_dataset):
    counts = ValueCountsProcessor("RainToday").process(sample_dataset)
    assert counts["No"] == 3
    assert counts["Yes"] == 2


def test_value_counts_processor_missing_column(sample_dataset):
    with pytest.raises(KeyError):
        ValueCountsProcessor("NotAColumn").process(sample_dataset)


# -- Data sources (fetching) --------------------------------------------------

def test_data_source_is_abstract():
    with pytest.raises(TypeError):
        DataSource()


def test_csv_file_data_source_missing_file(tmp_path):
    source = CsvFileDataSource(tmp_path / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        source.fetch()


def test_csv_file_data_source_fetch(tmp_path):
    path = tmp_path / "weather.csv"
    pd.DataFrame({"MinTemp": [1.0, 2.0]}).to_csv(path, index=False)

    source = CsvFileDataSource(path)
    df = source.fetch()
    assert list(df["MinTemp"]) == [1.0, 2.0]


def test_combined_csv_data_source(tmp_path):
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"

    pd.DataFrame({
        "id": ["Row0", "Row1"],
        "MinTemp": [10.0, 11.0],
        "RainTomorrow": [0, 1],
    }).to_csv(train_path, index=False)

    pd.DataFrame({
        "id": ["Row0", "Row1", "Row2"],
        "MinTemp": [9.0, 12.0, 13.0],
        # no RainTomorrow column here, mirrors a real train/test split
    }).to_csv(test_path, index=False)

    source = CombinedCsvDataSource([train_path, test_path])
    assert len(source) == 2  # __len__: number of files

    combined = source.fetch()
    assert len(combined) == 5
    assert "RainTomorrow" in combined.columns
    assert combined["RainTomorrow"].isna().sum() == 3
    assert set(combined["source_file"]) == {"train.csv", "test.csv"}


def test_combined_csv_data_source_requires_at_least_one_file():
    with pytest.raises(ValueError):
        CombinedCsvDataSource([])


# -- WeatherAnalysisApp (orchestration / composition) -------------------------

def test_app_from_directory_single_file(tmp_path):
    pd.DataFrame({"MinTemp": [1.0, 2.0, 3.0]}).to_csv(tmp_path / "weather.csv", index=False)

    app = WeatherAnalysisApp.from_directory(tmp_path)
    dataset = app.load()

    assert isinstance(dataset, WeatherDataset)
    assert len(dataset) == 3


def test_app_from_directory_multiple_files(tmp_path):
    pd.DataFrame({"MinTemp": [1.0, 2.0]}).to_csv(tmp_path / "a.csv", index=False)
    pd.DataFrame({"MinTemp": [3.0, 4.0]}).to_csv(tmp_path / "b.csv", index=False)

    app = WeatherAnalysisApp.from_directory(tmp_path)
    dataset = app.load()

    assert len(dataset) == 4


def test_app_from_directory_no_csvs(tmp_path):
    with pytest.raises(FileNotFoundError):
        WeatherAnalysisApp.from_directory(tmp_path)


def test_app_dataset_property_requires_load(tmp_path):
    pd.DataFrame({"MinTemp": [1.0]}).to_csv(tmp_path / "weather.csv", index=False)
    app = WeatherAnalysisApp.from_directory(tmp_path)
    with pytest.raises(RuntimeError):
        app.dataset  # load() hasn't been called yet


def test_app_run_processor(tmp_path):
    pd.DataFrame({"MinTemp": [1.0, 2.0, 3.0]}).to_csv(tmp_path / "weather.csv", index=False)
    app = WeatherAnalysisApp.from_directory(tmp_path)
    app.load()

    result = app.run_processor(DescriptiveStatsProcessor())
    assert result.loc["count", "MinTemp"] == 3
