"""Unit tests for the weatherstats package and main.py."""
import pandas as pd
import pytest
from pyspark.sql import SparkSession

import main
from weatherstats.data_sources import DataSource, CsvFileSource, CombinedCsvSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import StatsProcessor
from weatherstats.charts import WeatherCharts


def weather_frame():
    """Small DataFrame with the columns the analysis and charts use."""
    return pd.DataFrame({
        "Location": ["Sydney", "Sydney", "Perth", "Perth", "Darwin"],
        "MinTemp": [1.0, 2.0, 2.0, 3.0, 3.0],
        "MaxTemp": [10.0, 36.0, 30.0, 40.0, 50.0],
        "Rainfall": [0.0, 4.0, 0.0, 1.0, 10.0],
        "Humidity3pm": [40.0, 80.0, None, 50.0, 70.0],
        "RainToday": ["No", "Yes", "No", "No", "Yes"],
    })


def to_spark(spark, frame):
    """Turns a pandas DataFrame into a Spark DataFrame, with missing values as null."""
    rows = [tuple(None if pd.isna(value) else value for value in row) for row in frame.itertuples(index=False)]
    return spark.createDataFrame(rows, list(frame.columns))


@pytest.fixture(scope="session")
def spark():
    """One local Spark session shared by all the tests."""
    return SparkSession.builder.appName("WeatherStatsTests").master("local[*]").getOrCreate()


@pytest.fixture
def csv_files(tmp_path):
    """Two small csv files with the same columns as the weather data."""
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    data = weather_frame()
    data.iloc[:3].to_csv(first, index=False)
    data.iloc[3:].to_csv(second, index=False)
    return first, second


@pytest.fixture
def weather_processor(spark):
    """StatsProcessor over the small weather DataFrame."""
    return StatsProcessor(WeatherDataset(to_spark(spark, weather_frame())))


@pytest.fixture
def processor(spark):
    """StatsProcessor with a tie for the mode and one missing value."""
    data = pd.DataFrame({"MinTemp": [4.0, 1.0, 1.0, 3.0, 3.0, None]})
    return StatsProcessor(WeatherDataset(to_spark(spark, data)))


# data_sources.py

def test_data_source_cannot_be_created():
    with pytest.raises(TypeError):
        DataSource()


def test_csv_source_fetch_reads_all_rows(csv_files):
    data = CsvFileSource(csv_files[0]).fetch()
    assert len(data) == 3
    assert list(data.columns) == list(weather_frame().columns)


def test_csv_source_reads_in_chunks(csv_files):
    chunks = list(CsvFileSource(csv_files[0], chunksize=2).read_chunks())
    assert [len(chunk) for chunk in chunks] == [2, 1]


def test_csv_source_missing_file(tmp_path, caplog):
    with pytest.raises(FileNotFoundError):
        CsvFileSource(tmp_path / "nope.csv").fetch()
    assert "File not found" in caplog.text


def test_csv_source_empty_file(tmp_path, caplog):
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(pd.errors.EmptyDataError):
        CsvFileSource(empty).fetch()
    assert "Could not read" in caplog.text


def test_combined_source_fetch_combines_files(spark, csv_files):
    data = CombinedCsvSource(spark, [str(name) for name in csv_files]).fetch()
    assert data.count() == 5
    assert data.columns == list(weather_frame().columns)


def test_combined_source_missing_file(spark, tmp_path, caplog):
    with pytest.raises(FileNotFoundError):
        CombinedCsvSource(spark, [str(tmp_path / "nope.csv")]).fetch()
    assert "File not found" in caplog.text


# dataset.py

def test_dataset_from_source(spark, csv_files):
    dataset = WeatherDataset.from_source(CombinedCsvSource(spark, [str(name) for name in csv_files]))
    assert len(dataset) == 5
    assert str(dataset) == "WeatherDataset with 5 rows"


def test_dataset_data_is_read_only(processor):
    with pytest.raises(AttributeError):
        processor.dataset.data = pd.DataFrame()


def test_dataset_save_writes_csv(weather_processor, tmp_path):
    out_file = tmp_path / "out.csv"
    weather_processor.dataset.save(out_file)
    saved = pd.read_csv(out_file)
    assert len(saved) == 5
    assert list(saved.columns) == list(weather_frame().columns)


def test_dataset_save_bad_path(processor, tmp_path, caplog):
    with pytest.raises(OSError):
        processor.dataset.save(tmp_path / "missing_folder" / "out.csv")
    assert "Could not save" in caplog.text


# processors.py

def test_mean_skips_missing_values(processor):
    assert processor.calculate_mean("MinTemp") == pytest.approx(2.4)


def test_median(processor):
    assert processor.calculate_median("MinTemp") == 3.0


def test_mode_returns_lowest_on_tie(processor):
    assert processor.calculate_mode("MinTemp") == 1.0


def test_range(processor):
    assert processor.calculate_range("MinTemp") == 3.0


def test_missing_column(processor, caplog):
    with pytest.raises(KeyError):
        processor.calculate_mean("NotAColumn")
    assert "Column not found" in caplog.text


def test_average_skips_missing_values():
    assert StatsProcessor.average([2.0, None, 4.0]) == 3.0


def test_average_of_nothing_raises():
    with pytest.raises(ValueError):
        StatsProcessor.average([None])


def test_average_by_location(weather_processor):
    assert weather_processor.average_by_location("Rainfall") == {"Darwin": 10.0, "Perth": 0.5, "Sydney": 2.0}


# charts.py (the charts themselves are checked by looking at them)

def test_chart_bad_folder(weather_processor, tmp_path, caplog):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("")
    with pytest.raises(OSError):
        WeatherCharts(weather_processor, blocker).max_temp_histogram()
    assert "Could not save chart" in caplog.text


# main.py (these run last because main() stops the Spark session when it finishes)

def test_main_logs_error_when_files_missing(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    main.main()
    assert "Program stopped" in caplog.text
