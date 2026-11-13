'''Main is where we interact with all of the code in other files throughouth the program'''
import logging
import asyncio
from weatherstats.data_sources import CombinedCsvSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import StatsProcessor
from weatherstats.charts import WeatherCharts
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)

def main():
    '''Creation of the spark session.'''
    spark = SparkSession.builder.appName("WeatherStats").master("local[*]").getOrCreate()
    '''Changed this to utilize spark'''
    source = CombinedCsvSource(spark, ["WeatherData/Weather Training Data.csv", "WeatherData/Weather Test Data.csv"])
    try:
        data = source.fetch()
        dataset = WeatherDataset(data)
        dataset.save("output.csv")
        print(dataset)

        processor = StatsProcessor(dataset)
        for column, stats in processor.summarize(["MinTemp", "MaxTemp", "Rainfall"]):
            print(column)
            for name, value in stats.items():
                print(f"  {name}: {value}")

        hot_days = processor.filter_rows(lambda row: row.MaxTemp is not None and row.MaxTemp >= 35)
        rainy_days = processor.filter_rows(lambda row: row.RainToday == "Yes")
        print(f"Days at or above 35C: {len(hot_days)}")
        print(f"Rainy days: {len(rainy_days)}")
        print(f"Average 3pm humidity on rainy days: {processor.average_where('Humidity3pm', lambda row: row.RainToday == 'Yes'):.1f}%")
        print(f"Average 3pm humidity on dry days: {processor.average_where('Humidity3pm', lambda row: row.RainToday == 'No'):.1f}%")

        charts = WeatherCharts(processor)
        for make_chart in (charts.rainfall_by_location, charts.max_temp_histogram, charts.humidity_rain_vs_dry):
            print(f"Saved {make_chart()}")
    except (OSError, KeyError, ValueError) as error:
        logger.error("Program stopped: %s", error)
    finally:
        spark.stop()

    

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler("weatherstats.log"), logging.StreamHandler()],
    )
    main()
