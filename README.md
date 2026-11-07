# Weather Statistics

A small Python package that loads weather data from CSV files, stores it, calculates descriptive statistics like mean, median, mode, and range, and makes charts that show patterns in the weather.

## Dataset

**Australia Weather Data** from Kaggle:
https://www.kaggle.com/datasets/arunavakrchakraborty/australia-weather-data
`Weather Training Data.csv` and `Weather Test Data.csv` (142,193 rows combined)

Each row is one day of weather at one Australian location, with columns such as `MinTemp`, `MaxTemp`, `Rainfall`, `Humidity9am`, `WindGustSpeed`, and `RainToday`. The data has no date column, so patterns are looked at by location and by weather conditions instead of by time period.

## Setup

### Environment
- OS: Windows 11
- Python: 3.14
- IDE: VS Code (Python extension)
- Source control: Git, hosted on GitHub at https://github.com/Kingdomtily/Python-Software-Dev

### Install from source
From the project folder, with a virtual environment active:
pip install -e .


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
Days at or above 35C: 8174
Rainy days: 31455
Average 3pm humidity on rainy days: 66.2%
Average 3pm humidity on dry days: 47.2%
Saved charts\rainfall_by_location.png
Saved charts\max_temp_histogram.png
Saved charts\humidity_rain_vs_dry.png
The program also writes the combined data to `output.csv`, saves the charts to the `charts` folder, and writes log messages to the console and `weatherstats.log`.

### Module 5: Automated testing
- Wrote unit tests with pytest plus a doctest in `WeatherDataset`.
- Measured coverage with pytest-cov.
- Small refactor for testing: a docstring instead of `pass` in the abstract method.

### Module 6: Patterns, trends, and charts

#### Functional features
These were added to `StatsProcessor` in `processors.py`:
- `filter_rows(condition)` uses filter with a lambda passed in from `main.py` to pick out days of interest
- `average(values)` uses filter with a lambda to drop missing values
- `average_where(column, condition)` uses map with a lambda to pull one column out of the filtered rows, then averages it.
- `average_by_location(column)` uses map with a lambda to turn each location group into a `(location, average)` pair.
- The charts use `sorted` with a lambda key to find the wettest locations.

#### Charts
Made with matplotlib in the new `WeatherCharts` class (`charts.py`) and saved as PNG files:
1. Top 10 Wettest Locations (bar chart): shows which places get the most rain on an average day. 
2. Daily Maximum Temperature (histogram): shows how hot a typical day gets. 
3. Average 3pm Humidity: Rainy vs Dry Days (bar chart): checks whether humidity goes with rain.

### Module 7: Parallelism and Async

#### Parallelism
We implemented this change to calculate on separate cores. We couldn't do this witht threads due to Python's gil. This currently doesn't make a noticeable difference due to the dataset not being massive, but it should speed up the process. I chose to use ProcessPoolExecuter from concurrent.futures.
The code that utilizes this is `StatsProcessor.summarize_parallel_stats`

#### Asynchronous features
We added async features because reading files is I/O bound, so it ends up waiting on the disk. Async will let us load both files at once. Which again, should speed stuff up (not in too much of a noticeable way, but good to get the practice anyways.) I chose to use asyncio.gather and asyncio.to_thread from asyncio
The code that utilizes this is `CombinedCsvSource.async_fetch`

## Testing

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
| 18 | `test_filter_rows_with_lambda` | `filter_rows()` keeps only rows matching a lambda (hot days) |
| 19 | `test_average_skips_missing_values` | `average()` ignores empty values |
| 20 | `test_average_of_nothing_raises` | `average()` raises `ValueError` when there's nothing to average |
| 21 | `test_average_where` | Humidity averages for rainy and dry days are correct |
| 22 | `test_average_by_location` | Averages per location are correct |
| 23 | `test_charts_are_saved` | All three charts are saved as PNG files |
| 24 | `test_chart_bad_folder` | A chart that can't be saved raises `OSError` and logs it |
| 25 | `test_main_prints_stats` | `main()` prints the stats and patterns, writes `output.csv`, and saves 3 charts |
| 26 | `test_main_logs_error_when_files_missing` | `main()` logs "Program stopped" instead of crashing |
| 27 | Doctest in `WeatherDataset` | `print(dataset)` shows the row count |
| 28 | `test_combined_source_async_fetch_matches_fetch` | Double checks that the async outputs the same value as the sync
| 29 | `test_summarize_parallel_matches_summarize` | Double checks that the output of this new function matches the old one
Result: 29 passed

## Documentation
API documentation is generated from the docstrings with pydoc:
python -m pydoc -w weatherstats weatherstats.data_sources weatherstats.dataset weatherstats.processors weatherstats.charts

## License
MIT. See `LICENSE`.
