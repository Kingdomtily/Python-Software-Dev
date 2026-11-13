"""Class for calculating statistics on a WeatherDataset."""
import logging
import math
from functools import reduce
from concurrent.futures import ProcessPoolExecutor
from pyspark.sql import functions as F

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
        return self.dataset.data.rdd.filter(condition).collect()

    @staticmethod
    def average(values):
        """Averages numbers with reduce, skipping missing values."""
        numbers = list(filter(lambda value: value is not None, values))
        if not numbers:
            raise ValueError("No values to average")
        return reduce(lambda total, value: total + value, numbers) / len(numbers)

    def average_where(self, column, condition):
        """Averages a column over only the rows where condition(row) is True."""
        rows = self.filter_rows(condition)
        return self.average(map(lambda row: getattr(row, column), rows))

    def average_by_location(self, column):
        """Returns {location: average of column}, built with map and a lambda."""
        rows = self.dataset.data.groupBy("Location").agg(F.avg(self._column(column))).collect()
        return dict(map(lambda row: (row[0], row[1]), rows))
    def _column(self, column):
        if column not in self.dataset.data.columns:
            logger.error("Column not found: %s", column)
            raise KeyError(column)
        return column

    def calculate_mean(self, column):
        return self.dataset.data.select(F.mean(self._column(column))).first()[0]

    def calculate_median(self, column):
        return self.dataset.data.approxQuantile(self._column(column), [0.5], 0.0)[0]

    def calculate_mode(self, column):
        """Returns the lowest value if there is a tie."""
        col = self._column(column)
        return (self.dataset.data.filter(F.col(col).isNotNull())
                .groupBy(col).count()
                .orderBy(F.desc("count"), F.asc(col))
                .first()[0])

    def calculate_range(self, column):
        row = self.dataset.data.select(F.max(self._column(column)), F.min(column)).first()
        return row[0] - row[1]