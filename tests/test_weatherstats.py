"""Unit tests for the weatherstats package and main.py."""
import pandas as pd
import pytest

import main
from weatherstats.data_sources import DataSource, CsvFileSource, CombinedCsvSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import StatsProcessor


@pytest.fixture
def csv_files(tmp_path):
    """Two small csv files with the same columns as the weather data."""
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    pd.DataFrame({"MinTemp": [1.0, 2.0, 2.0], "MaxTemp": [10.0, 20.0, 30.0], "Rainfall": [0.0, 0.0, 5.0]}).to_csv(first, index=False)
    pd.DataFrame({"MinTemp": [3.0, 3.0], "MaxTemp": [40.0, 50.0], "Rainfall": [1.0, 0.0]}).to_csv(second, index=False)
    return first, second


@pytest.fixture
def processor():
    """StatsProcessor with a tie for the mode and one missing value."""
    data = pd.DataFrame({"MinTemp": [4.0, 1.0, 1.0, 3.0, 3.0, None]})
    return StatsProcessor(WeatherDataset(data))


# data_sources.py

def test_data_source_cannot_be_created():
    with pytest.raises(TypeError):
        DataSource()


def test_csv_source_fetch_reads_all_rows(csv_files):
    data = CsvFileSource(csv_files[0]).fetch()
    assert len(data) == 3
    assert list(data.columns) == ["MinTemp", "MaxTemp", "Rainfall"]


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


def test_combined_source_iterates_one_frame_per_file(csv_files):
    frames = list(CombinedCsvSource(csv_files))
    assert [len(frame) for frame in frames] == [3, 2]


def test_combined_source_fetch_combines_files(csv_files):
    data = CombinedCsvSource(csv_files).fetch()
    assert len(data) == 5
    assert list(data.index) == [0, 1, 2, 3, 4]


# dataset.py

def test_dataset_from_source(csv_files):
    dataset = WeatherDataset.from_source(CombinedCsvSource(csv_files))
    assert len(dataset) == 5
    assert str(dataset) == "WeatherDataset with 5 rows"


def test_dataset_data_is_read_only(processor):
    with pytest.raises(AttributeError):
        processor.dataset.data = pd.DataFrame()


def test_dataset_save_writes_csv(csv_files, tmp_path):
    dataset = WeatherDataset.from_source(CsvFileSource(csv_files[0]))
    out_file = tmp_path / "out.csv"
    dataset.save(out_file)
    assert pd.read_csv(out_file).equals(dataset.data)


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


def test_summarize_yields_one_column_at_a_time(processor):
    results = processor.summarize(["MinTemp", "MinTemp"])
    column, stats = next(results)
    assert column == "MinTemp"
    assert stats == {"mean": pytest.approx(2.4), "median": 3.0, "mode": 1.0, "range": 3.0}
    assert len(list(results)) == 1


# main.py

def test_main_prints_stats(csv_files, tmp_path, monkeypatch, capsys):
    folder = tmp_path / "WeatherData"
    folder.mkdir()
    csv_files[0].rename(folder / "Weather Training Data.csv")
    csv_files[1].rename(folder / "Weather Test Data.csv")
    monkeypatch.chdir(tmp_path)
    main.main()
    output = capsys.readouterr().out
    assert "WeatherDataset with 5 rows" in output
    assert "Rainfall" in output
    assert (tmp_path / "output.csv").exists()


def test_main_logs_error_when_files_missing(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    main.main()
    assert "Program stopped" in caplog.text
