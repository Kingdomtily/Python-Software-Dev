# Weather Data Analysis — Code Overview

This project loads a weather CSV with pandas and prints descriptive statistics on it. The code is split into a small package (`weatherstats`) plus a driver script (`main.py`) that imports and uses it like any other library.

## `src/weatherstats/data_loader.py`

Handles reading CSV files into pandas.

- `_read_header(csv_path)` — reads just a CSV's column names, no data rows.
- `load_weather_data(csv_path, usecols=None)` — loads one CSV into a DataFrame. Parses a date column if one exists; errors clearly if the file is missing.
- `load_and_combine_weather_data(csv_paths)` — loads multiple CSVs and combines them into one DataFrame (e.g. a train + test split). Adds a `source_file` column so you can tell which file each row came from.
- `numeric_columns(df)` — returns the names of a DataFrame's numeric columns.

## `src/weatherstats/stats.py`

Computes statistics on an already-loaded DataFrame.

- `descriptive_stats(df, columns=None)` — the main function. Returns a table of count, mean, median, mode, standard deviation, min, max, and range for each numeric column.
- `value_counts_summary(df, column, top_n=5)` — for a text column (like `RainToday`), returns the most common values and how often each appears.

## `src/weatherstats/__init__.py`

Re-exports the functions above so you can just write `import weatherstats as ws` and call `ws.load_weather_data(...)`, `ws.descriptive_stats(...)`, etc., instead of digging into individual files.

## `main.py`

The script you run.

- `load_dataset()` — finds every CSV in `data/` and loads it; combines them automatically if there's more than one.
- `main()` — loads the data, prints the record count, and prints the descriptive statistics table.

## `tests/test_weatherstats.py`

Automated checks using fake/temporary data (no real dataset needed) confirming `descriptive_stats`, `value_counts_summary`, `load_weather_data`, and `load_and_combine_weather_data` all behave as expected.
