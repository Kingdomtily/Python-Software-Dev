"""Classes for fetching data from csv files."""
from abc import ABC, abstractmethod
import pandas as pd

class DataSource(ABC):
    """Base class, every data source must have a fetch method."""
    @abstractmethod
    def fetch(self):
        pass

class CsvFileSource(DataSource):
    """Fetches data from a single csv file."""
    def __init__(self, filename):
        self.filename = filename

    def fetch(self):
        return pd.read_csv(self.filename)

class CombinedCsvSource(DataSource):
    """Fetches several csv files and combines them into one DataFrame."""
    def __init__(self, filenames):
        self.sources = [CsvFileSource(name) for name in filenames]

    def fetch(self):
        return pd.concat([source.fetch() for source in self.sources], ignore_index=True)
