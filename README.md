# Weather Data Analysis (Modules 1 & 2)

A small, professionally-structured Python project that loads an
Australian weather dataset from Kaggle, computes descriptive
statistics on it, and packages that logic as an installable library
(`weatherstats`) instead of a single monolithic script.

## Description

This repo covers two course modules:

- **Module 1** -- set up a professional Python development
  environment with source control, fetch weather data from a CSV into
  Python, and document the code (docstrings, pydoc, this README).
- **Module 2** -- switch the CSV loading over to `pandas`, compute
  descriptive statistics (mean, median, mode, standard deviation, min,
  max, range), and **modularize** the code into a real, pip-installable
  package (`weatherstats`) that's built and used the same way you'd use
  any official third-party library.

The dataset is the Kaggle **"Rain in Australia"** weather data. This
project supports either shape it's commonly distributed in:

- a single `weatherAUS.csv` with a `Date` column, or
- a pre-split `Weather Training Data.csv` + `Weather Test Data.csv`
  pair indexed by `row ID` (used here -- the training split alone is
  ~99.5k rows, just under the assignment's 100k-record minimum, so
  `main.py` combines both files to reach 142,193 total records).

## Development environment setup

Documenting this was part of the Module 1 assignment. This project was
built with:

- **Python 3.11**, run from the command line (`python3 …`) rather than
  through an IDE's "run" button -- getting comfortable with the
  terminal was an explicit goal of Module 1.
- **A virtual environment** for dependency isolation:
  `python3 -m venv .venv && source .venv/bin/activate` (see
  Installation below). If your environment already has `pandas`/
  `setuptools` available system-wide, a venv is optional but still
  good practice.
- **Git** for source control, initialized from the start of the
  project (`git init`), with incremental commits as functionality was
  added (see `git log` in this repo) rather than one giant commit at
  the end.
- **An editor with Python tooling**: VS Code with the Python and
  Pylance extensions (or PyCharm) for linting, autocomplete, and
  inline docstring/type-hint support -- but all actual project
  commands (installing, running, testing, generating docs) are run
  from the terminal, not editor buttons, per the "power users use the
  terminal" guidance in the assignment.
- **pydoc** (Python's built-in documentation generator) for API docs --
  see `docs/pydoc/index.html`, regenerated with
  `scripts/generate_docs.sh`.
- **pytest** for unit tests (`tests/test_weatherstats.py`).

## Project structure

```
weather-module2/
├── pyproject.toml            # package metadata / build config
├── main.py                   # Module 2 driver script
├── README.md                 # this file
├── .gitignore
├── data/
│   └── (place the Kaggle CSV(s) here -- not committed to git)
├── docs/
│   └── pydoc/                # generated API docs (see below)
├── scripts/
│   └── generate_docs.sh      # regenerates docs/pydoc/
├── src/
│   └── weatherstats/         # the package itself
│       ├── __init__.py       # public API (re-exports)
│       ├── data_loader.py    # loading CSV(s) with pandas
│       ├── stats.py          # descriptive statistics
│       └── report.py         # turns stats into a printable report
└── tests/
    └── test_weatherstats.py  # pytest unit tests (in-memory data, no CSV needed)
```

## Installation

```bash
git clone <this-repo-url>
cd weather-module2

# optional but recommended: an isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"          # installs weatherstats + pytest
```

`pip install -e .` builds `weatherstats` from `pyproject.toml` /
`src/weatherstats` and installs it in "editable" mode: it behaves like
a normal installed library (`import weatherstats`) anywhere in this
environment, while still picking up source edits without reinstalling.
This is the "build and publish a package" / "install and use it like
an official library" step from the Module 2 assignment.

## Getting the dataset

1. Download a Kaggle "Rain in Australia" weather dataset, e.g.
   https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package
   (single `weatherAUS.csv`), or the pre-split
   "Weather Dataset Rattle Package" variant used during development
   here (`Weather Training Data.csv` + `Weather Test Data.csv`).
2. Place the CSV(s) in `data/`:
   - `data/weatherAUS.csv`, **or**
   - `data/Weather Training Data.csv` and
     `data/Weather Test Data.csv`.

`main.py` auto-detects which shape is present. If only the training
split is around, it still works, but you'll see a warning that it's
under the 100k-record minimum -- add the test split alongside it (or
use the single-file version) to clear that bar.

## Usage

```bash
python main.py
```

This will:
1. Import `weatherstats` (the installed package, not a local include).
2. Load the CSV(s) in `data/` via `pandas.read_csv` under the hood,
   combining the train/test split if that's what's present.
3. Compute descriptive statistics (count, mean, median, mode, standard
   deviation, min, max, range) for the numeric weather columns.
4. Print a formatted report, and confirm the record count meets the
   100k minimum.

### Running the tests

```bash
pytest
```

`tests/test_weatherstats.py` tests the `data_loader`, `stats`, and
`report` modules directly -- including the train/test-combining logic
-- against small in-memory/temp-file data, so it runs instantly without
needing the full dataset downloaded.

### Generating the docs

```bash
scripts/generate_docs.sh
```

Runs `python -m pydoc -w` over each module and writes HTML into
`docs/pydoc/`. Open `docs/pydoc/index.html` in a browser to view.

## How this satisfies the assignments

- **Source control**: this is a git repository with incremental
  commits, not a single dump of files.
- **Fetch + document + pydoc + README (Module 1)**: data is fetched
  from CSV via pandas, every module/function has a docstring, API docs
  are generated with the built-in `pydoc` tool into `docs/pydoc/`, and
  this README documents the setup, following the makeareadme.com
  template.
- **pandas + Kaggle CSV (Module 2)**: `data_loader.py` uses
  `pandas.read_csv` to read the downloaded dataset(s), including
  combining a train/test split to clear the 100k-record minimum.
- **Descriptive statistics**: `stats.py`'s `descriptive_stats()`
  computes count, mean, median, mode, standard deviation, min, max,
  and range for every numeric column.
- **Modularization**: the code is split into independent modules
  (loading / stats / reporting) inside a real installable package,
  rather than one monolithic script.
- **Install and use it like an official library**: `main.py` does
  `import weatherstats as ws` and calls `ws.load_weather_data(...)`,
  `ws.generate_summary_report(...)`, etc. -- exactly like using
  `pandas` or `numpy` -- never reaching into the package's source tree.

### Optional: publishing to PyPI for real

The local `pip install -e .` workflow above satisfies "build and
publish a package" without needing external credentials. If you want
an actually-public package, you can additionally push it to
**TestPyPI**:

```bash
pip install build twine
python -m build
twine upload --repository testpypi dist/*
```

This needs a free TestPyPI account and API token
(https://test.pypi.org/manage/account/#api-tokens); afterward anyone
could `pip install -i https://test.pypi.org/simple/ weatherstats`.
Optional, not required for the workflow above.

## Roadmap

Later modules in this course build on this same dataset and package,
so `weatherstats` is expected to grow new modules (e.g. data cleaning,
visualization, or modeling helpers) without changing how `main.py`
imports and uses it.

## Author

Tyler Francom

## Project status

Modules 1 and 2 complete.
