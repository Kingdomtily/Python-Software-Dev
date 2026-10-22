# Weather Statistics

A small Python package that loads weather data from CSV files, stores it, and calculates descriptive statistics like mean, median, mode, and range.

## Dataset

**Australia Weather Data** from Kaggle:
https://www.kaggle.com/datasets/arunavakrchakraborty/australia-weather-data
`Weather Training Data.csv` and `Weather Test Data.csv`

Each row is one day of weather at one Australian location, with columns such as `MinTemp`, `MaxTemp`, `Rainfall`, `Humidity9am`, `WindGustSpeed`, and `RainToday`

## Setup

### Environment
- OS: Windows 11
- Python: 3.14
- IDE: VS Code (Python extension)
- Source control: Git, hosted on GitHub at https://github.com/Kingdomtily/Python-Software-Dev

### Install from TestPyPI
The package was published to TestPyPI:
https://test.pypi.org/project/weatherstats-kingdomtily/

pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ weatherstats-kingdomtily


## Usage
python main.py

Example output:
WeatherDataset with 142193 rows
MinTemp
  mean: 12.186399728729267
  median: 12.0
  mode: 9.6
  range: 42.4
MaxTemp
  mean: 23.226784191272355
  median: 22.6
  mode: 20.0
  range: 52.9
Rainfall
  mean: 2.3499740743108384
  median: 0.0
  mode: 0.0
  range: 371.0

The program also writes the combined data to `output.csv` and writes log messages to the console and `weatherstats.log`.

### Module 5: Automated testing
- Wrote unit tests with **pytest** plus a **doctest** in `WeatherDataset`.
- Measured coverage with **pytest-cov**: 100% of the package and `main.py`.
- Small refactors for testing: a docstring instead of `pass` in the abstract method, and `# pragma: no cover` on the `if __name__ == "__main__":` block.

Run the tests:
pip install pytest pytest-cov
pytest --cov=weatherstats --cov=main --cov-report=term-missing

#### Test cases

| # | Test | What it checks |
| 1 | `test_data_source_cannot_be_created` | The abstract `DataSource` can't be created directly |
| 2 | `test_csv_source_fetch_reads_all_rows` | `fetch()` returns every row and column |
| 3 | `test_csv_source_reads_in_chunks` | `read_chunks()` yields the right chunk sizes |
| 4 | `test_csv_source_missing_file` | A missing file raises `FileNotFoundError` and logs it |
| 5 | `test_csv_source_empty_file` | An empty CSV raises `EmptyDataError` and logs it |
| 6 | `test_combined_source_iterates_one_frame_per_file` | Looping yields one DataFrame per file |
| 7 | `test_combined_source_fetch_combines_files` | Files are combined and rows renumbered |
| 8 | `test_dataset_from_source` | `from_source()`, `len()`, and `str()` work |
| 9 | `test_dataset_data_is_read_only` | `data` can't be replaced |
| 10 | `test_dataset_save_writes_csv` | `save()` writes matching data |
| 11 | `test_dataset_save_bad_path` | Saving to a missing folder raises `OSError` and logs it |
| 12 | `test_mean_skips_missing_values` | Mean ignores empty values |
| 13 | `test_median` | Median is correct |
| 14 | `test_mode_returns_lowest_on_tie` | Ties return the lowest value |
| 15 | `test_range` | Range is max minus min |
| 16 | `test_missing_column` | An unknown column raises `KeyError` and logs it |
| 17 | `test_summarize_yields_one_column_at_a_time` | `summarize()` yields one column per step |
| 18 | `test_main_prints_stats` | `main()` prints stats and writes `output.csv` |
| 19 | `test_main_logs_error_when_files_missing` | `main()` logs "Program stopped" instead of crashing |
| 20 | Doctest in `WeatherDataset` | `print(dataset)` shows the row count |

Result: **20 passed, 100% coverage.**

## Documentation
API documentation is generated from the docstrings with pydoc:
python -m pydoc -w weatherstats weatherstats.data_sources weatherstats.dataset weatherstats.processors

## License
MIT. See `LICENSE`.