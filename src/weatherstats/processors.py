"""Class for calculating statistics on a WeatherDataset."""
import logging

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
