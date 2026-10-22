"""Class for storing the weather data."""
import logging

logger = logging.getLogger(__name__)

class WeatherDataset:
    """Holds the weather data and can save it to a csv file."""
    def __init__(self, data):
        self._data = data

    @classmethod
    def from_source(cls, source):
        """Creates a dataset using the data from a DataSource."""
        return cls(source.fetch())

    @property
    def data(self):
        return self._data

    def save(self, filename):
        """Writes the data to a csv file."""
        try:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                self._data.to_csv(file, index=False)
        except OSError as error:
            logger.error("Could not save to %s: %s", filename, error)
            raise
        logger.info("Saved %d rows to %s", len(self), filename)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return f"WeatherDataset with {len(self)} rows"
