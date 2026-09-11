# Weather Data Analysis — Phase 3 Design Notes

Phase 2 was a small library of free functions: one file to load CSVs,
another to compute statistics, and a driver script that called both. It
worked, but nothing about it was an object — data just flowed through
functions as a bare `pandas.DataFrame`.

Phase 3 refactors that same behavior into classes, organized around the
three jobs the instructions called out: **fetching** data, **storing** it,
and **processing** it. Each job got its own small module instead of one
big one, so a class only has to know about its own job.

```
src/weatherstats/
    data_sources.py   -- fetching:   DataSource, CsvFileDataSource, CombinedCsvDataSource
    dataset.py         -- storage:    WeatherDataset
    processors.py       -- processing: StatsProcessor, DescriptiveStatsProcessor, ValueCountsProcessor
    app.py              -- orchestration: WeatherAnalysisApp
    __init__.py
```

## Fetching: `data_sources.py`

`DataSource` is an abstract base class (built with Python's `abc`
module — `ABC` and `@abstractmethod`). It declares one method,
`fetch() -> DataFrame`, and can't be instantiated on its own
(`DataSource()` raises `TypeError`). That's the point of an ABC: it's a
contract, not a usable object.

`CsvFileDataSource` and `CombinedCsvDataSource` both inherit from
`DataSource` and each implement `fetch()` in their own way — one reads a
single file, the other reads several and concatenates them. Because both
honor the same interface, `WeatherAnalysisApp` (see below) can hold
either one and just call `.fetch()` without caring which it has. That's
polymorphism: the same method call does the right thing depending on
the actual object's type.

`CombinedCsvDataSource` doesn't re-implement file-reading itself — it
builds a list of `CsvFileDataSource` objects internally and delegates to
them. That's composition (one object holding and using other
objects) rather than inheritance, chosen because a "combined" source
*has* several single-file sources, it isn't a kind of one.

## Storage: `dataset.py`

`WeatherDataset` wraps a `DataFrame` instead of passing it around bare.
This is encapsulation: the frame lives in a "private" `_data`
attribute (the leading underscore is Python's convention for "internal,
please don't touch directly") and is only exposed through a read-only
`@property`. There's deliberately no setter — once a dataset is built,
swapping its data out from outside isn't something the class allows.
The constructor also validates what it's given (must be a non-empty
DataFrame) before accepting it, so a bad dataset can't be created
half-formed.

It also implements several dunder methods so a
`WeatherDataset` plugs into normal Python syntax instead of needing its
own special-purpose methods for everything:

- `__len__` → `len(dataset)` gives the record count
- `__repr__` / `__str__` → unambiguous vs. human-readable printing
- `__eq__` → `dataset_a == dataset_b` compares contents, not identity

`WeatherDataset.from_data_source(...)` is a class method used as an
alternate constructor: the normal `__init__` expects data you already
have in hand, while this one takes a `DataSource` and does the fetching
for you, then builds the instance. Two ways to construct the same kind of
object, for two different starting points.

## Processing: `processors.py`

Mirrors the fetching side on purpose: `StatsProcessor` is another
abstract base class with one method, `process(dataset)`.
`DescriptiveStatsProcessor` (count/mean/median/mode/std/min/max/range)
and `ValueCountsProcessor` (top-N values of a categorical column) both
inherit from it and implement `process()` differently — again,
polymorphism lets `WeatherAnalysisApp.run_processor(...)` accept any of
them interchangeably. Each processor is configured in its constructor
(which columns, which column and how many top values) and holds that
configuration as instance state, so the same processor object can be
reused across multiple datasets.

## Orchestration: `app.py`

`WeatherAnalysisApp` doesn't fetch, store, or process anything itself —
it composes a `DataSource`, a `WeatherDataset`, and whatever
`StatsProcessor`s it's handed, and coordinates them: `load()` fetches and
wraps the data, `run_processor(...)` runs an analysis against whatever's
loaded. This is a HAS-A relationship (an app *has* a data source) rather
than an IS-A one, which is why it doesn't inherit from `DataSource` —
composition was the right tool here, not inheritance.

`MIN_REQUIRED_RECORDS` is a class variable (`100_000`, shared by every
`WeatherAnalysisApp` instance as a default) rather than something each
instance has to set for itself. `from_directory(...)` is another
classmethod alternate constructor — same idea as `WeatherDataset`'s —
that knows how to turn "every CSV in this folder" into the right kind of
`DataSource` (single-file vs. combined) and hand back a ready-to-use app.

## `main.py`

With all of that in place, the driver script is just a few lines:
build an app from the data directory, load it, print it (`__str__` does
the formatting), check the minimum, and run a `DescriptiveStatsProcessor`
over it. None of the "how" lives here anymore — just the sequence of
steps.

## What Chapter 3 features were not used, and why

Operator overloading beyond `__eq__` (e.g. `__add__` to merge two
datasets) and multiple inheritance weren't needed here — there was no
natural "add two datasets together" operation in this assignment's scope,
and every class had a single, clear parent. Property *setters* with
validation were considered for `WeatherDataset`, but the design calls for
data to be immutable once loaded, so a read-only property fit better than
a validated setter. These are reasonable fits for later phases if the
application grows in those directions.

## Running it

```bash
pip install -e ".[dev]"
python main.py
pytest
```
