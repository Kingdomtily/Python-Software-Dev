"""Classes for fetching data from csv files."""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import asyncio

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """Base class, every data source must have a fetch method."""
    @abstractmethod
    def fetch(self):
        """Returns the data as a DataFrame."""

class CsvFileSource(DataSource):
    """Fetches data from a single csv file."""
    def __init__(self, filename, chunksize=10000):
        self.filename = filename
        self.chunksize = chunksize

    def read_chunks(self):
        """Generator that yields the file in chunks of rows instead of all at once."""
        if not Path(self.filename).is_file():
            logger.error("File not found: %s", self.filename)
            raise FileNotFoundError(f"Could not find {self.filename}")
        logger.info("Reading %s", self.filename)
        try:
            with pd.read_csv(self.filename, chunksize=self.chunksize) as reader:
                for chunk in reader:
                    yield chunk
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
            logger.error("Could not read %s: %s", self.filename, error)
            raise

    def fetch(self):
        return pd.concat(self.read_chunks(), ignore_index=True)

class CombinedCsvSource(DataSource):
    """Fetches several csv files and combines them into one DataFrame."""
    def __init__(self, filenames):
        self.sources = [CsvFileSource(name) for name in filenames]

    def __iter__(self):
        """Lets you loop over the source, yielding one DataFrame per file."""
        for source in self.sources:
            yield source.fetch()

    def fetch(self):
        data = pd.concat(self, ignore_index=True)
        logger.info("Combined %d files into %d rows", len(self.sources), len(data))
        return data

    async def async_fetch(self):
        """"Designed to read both CSVs at the same time, as an async"""
        frames = await asyncio.gather(*(asyncio.to_thread(source.fetch)for source in self.sources))
        data = pd.concat(frames, ignore_index=True)
        return data
