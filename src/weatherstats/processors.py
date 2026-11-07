"""Class for calculating statistics on a WeatherDataset."""
import logging
import math
from functools import reduce
from concurrent.futures import ProcessPoolExecutor

logger = logging.getLogger(__name__)

class StatsProcessor:
    """Calculates statistics on one column of a WeatherDataset."""
    def __init__(self, dataset):
        self.dataset = dataset

    def _column(self, column):
        try:
            return self.dataset.data[column]
        except KeyError:
            logger.error("Column not found: %s", column)
            raise

    def calculate_mean(self, column):
        return self._column(column).mean()

    def calculate_median(self, column):
        return self._column(column).median()

    def calculate_mode(self, column):
        """Returns the lowest value if there is a tie."""
        return self._column(column).mode().iloc[0]

    def calculate_range(self, column):
        return self._column(column).max() - self._column(column).min()

    def summarize(self, columns):
        """Generator that yields (column, stats) for one column at a time."""
        for column in columns:
            logger.info("Calculating stats for %s", column)
            yield column, {
                "mean": self.calculate_mean(column),
                "median": self.calculate_median(column),
                "mode": self.calculate_mode(column),
                "range": self.calculate_range(column),
            }

    def filter_rows(self, condition):
        """Returns the rows where condition(row) is True, using filter."""
        return list(filter(condition, self.dataset.data.itertuples(index=False)))

    @staticmethod
    def average(values):
        """Averages numbers with reduce, skipping missing values."""
        numbers = list(filter(lambda value: not math.isnan(value), values))
        if not numbers:
            raise ValueError("No values to average")
        return reduce(lambda total, value: total + value, numbers) / len(numbers)

    def average_where(self, column, condition):
        """Averages a column over only the rows where condition(row) is True."""
        rows = self.filter_rows(condition)
        return self.average(map(lambda row: getattr(row, column), rows))

    def average_by_location(self, column):
        """Returns {location: average of column}, built with map and a lambda."""
        groups = self._column(column).groupby(self._column("Location"))
        return dict(map(lambda item: (item[0], item[1].mean()), groups))

    def summarize_parallel_stats(self, columns):
        with ProcessPoolExecutor() as executor:
            return list(executor.map(parallel_stats, columns, [self._column(c) for c in columns]))

def parallel_stats(column, values):
    """Used to do the column statistics in parallel. Designed to do one column per process"""
    return column, {
        "mean": values.mean(),
        "median": values.median(),
        "mode": values.mode().iloc[0],
        "range": values.max() - values.min()
    }
