"""Class for making charts of the weather data with matplotlib."""
import logging
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class WeatherCharts:
    """Creates charts from a StatsProcessor and saves them as png files."""
    def __init__(self, processor, folder="charts"):
        self.processor = processor
        self.folder = Path(folder)

    def _save(self, figure, name):
        path = self.folder / name
        try:
            self.folder.mkdir(exist_ok=True)
            figure.savefig(path)
        except OSError as error:
            logger.error("Could not save chart %s: %s", path, error)
            raise
        finally:
            plt.close(figure)
        logger.info("Saved chart %s", path)
        return path

    def rainfall_by_location(self, top=10):
        """Bar chart of the locations with the highest average daily rainfall."""
        averages = self.processor.average_by_location("Rainfall")
        wettest = sorted(averages.items(), key=lambda item: item[1], reverse=True)[:top]
        figure, axes = plt.subplots(figsize=(10, 5))
        axes.bar([name for name, _ in wettest], [value for _, value in wettest])
        axes.set_title(f"Top {top} Wettest Locations")
        axes.set_ylabel("Average daily rainfall (mm)")
        axes.tick_params(axis="x", rotation=45)
        figure.tight_layout()
        return self._save(figure, "rainfall_by_location.png")

    def max_temp_histogram(self):
        """Histogram of how often each maximum temperature happens."""
        figure, axes = plt.subplots()
        axes.hist(self.processor.dataset.data.select("MaxTemp").dropna().toPandas()["MaxTemp"], bins=40)
        axes.set_title("Daily Maximum Temperature")
        axes.set_xlabel("Max temperature (C)")
        axes.set_ylabel("Number of days")
        return self._save(figure, "max_temp_histogram.png")

    def humidity_rain_vs_dry(self):
        """Bar chart comparing 3pm humidity on rainy days and dry days."""
        rainy = self.processor.average_where("Humidity3pm", lambda row: row.RainToday == "Yes")
        dry = self.processor.average_where("Humidity3pm", lambda row: row.RainToday == "No")
        figure, axes = plt.subplots()
        axes.bar(["Rainy days", "Dry days"], [rainy, dry], color=["tab:blue", "tab:orange"])
        axes.set_title("Average 3pm Humidity: Rainy vs Dry Days")
        axes.set_ylabel("Humidity (%)")
        return self._save(figure, "humidity_rain_vs_dry.png")
