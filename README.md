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
This project is now a webapp, and has a different way of running it. First java needs to be installed, then you run pip install -e . then you run python app.py. This will then direct you to open http://127.0.0.1:5000. startup will take about 30 ish seconds.

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

### Module 8: PySpark

#### Where It Runs:
Google collab with Spark in local mode as the virtual cluster. Spark will split the work in the machine's cores as a simulation of a real cluster splitting it across machines.

#### How to run:
```
!pip install pyspark
!git clone -b master https://github.com/Kingdomtily/Python-Software-Dev.git
%cd Python-Software-Dev
!pip install .
!python main.py
```

#### What I changed:
Main creats a spark session and stops it with finally, data_sources.py reads the csvs with spark.read.csv and combines them. Processors.py uses spark functions, such as F.mean, approxQuantile, and groupBy().count(). Dataset.py utilizes count() instead of len() because pyspark doesnt have a len() function. I also removed the processpoolexecutor and the asyncio loading due to Spark being able to do all of that work itself. summarize_parallel_stats and async_fetch were replaced this module.

#### What I had to consider:
Some of the methods used Spark did not have. Like I mentioned above, len didn't exist, as well as the pandas methods .median(), .mode(), and itertuples. Some things were needed for proper loading, like inferSchema=True. The missing values are different, rather than being NaN, it was None. So the hot days filter and average had to check for None rather than NaN.

#### Results:
After a few issues to get ironed out, the output is the same as before.

### Module 9: Webapp

#### How to run:
I have updated the instructions above to describe how to run this project. It does take a second to start up, I believe it takes Spark a moment to startup before running.

#### 3-tier description:
The three tiers are the UI, which is in the templates/ and static/style.css files. Business logic, whis is in app.py and src/weatherstats/ and database, models.py uses sqlite through flask-sqlalchemy. It stores each search's location, column, stats, and time to recall for the history 

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
| 6 | `test_combined_source_fetch_combines_files` | Spark combines both files into one DataFrame with all rows |
| 7 | `test_combined_source_missing_file` | The Spark source raises `FileNotFoundError` for a missing file and logs it |
| 8 | `test_dataset_from_source` | `from_source()`, `len()`, and `str()` work |
| 9 | `test_dataset_data_is_read_only` | `data` can't be replaced |
| 10 | `test_dataset_save_writes_csv` | `save()` writes a CSV with every row and column |
| 11 | `test_dataset_save_bad_path` | Saving to a missing folder raises `OSError` and logs it |
| 12 | `test_mean_skips_missing_values` | Mean ignores empty values |
| 13 | `test_median` | Median is correct |
| 14 | `test_mode_returns_lowest_on_tie` | Ties return the lowest value |
| 15 | `test_range` | Range is max minus min |
| 16 | `test_missing_column` | An unknown column raises `KeyError` and logs it |
| 17 | `test_average_skips_missing_values` | `average()` ignores empty values |
| 18 | `test_average_of_nothing_raises` | `average()` raises `ValueError` when there's nothing to average |
| 19 | `test_average_by_location` | Averages per location are correct |
| 20 | `test_chart_bad_folder` | A chart that can't be saved raises `OSError` and logs it |
| 21 | `test_main_logs_error_when_files_missing` | `main()` logs "Program stopped" instead of crashing |
Result: 21 passed (the tests take a few minutes because Spark starts locally)

## Documentation
API documentation is generated from the docstrings with pydoc:
python -m pydoc -w weatherstats weatherstats.data_sources weatherstats.dataset weatherstats.processors weatherstats.charts

## License
MIT. See `LICENSE`.
