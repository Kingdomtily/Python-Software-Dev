'''Main is where we interact with all of the code in other files throughouth the program'''
import logging
from weatherstats.data_sources import CombinedCsvSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import StatsProcessor

logger = logging.getLogger(__name__)

def main():
    '''Main function to include all of the program's instructions'''
    source = CombinedCsvSource(["WeatherData/Weather Training Data.csv", "WeatherData/Weather Test Data.csv"])
    try:
        dataset = WeatherDataset.from_source(source)
        dataset.save("output.csv")
        print(dataset)

        processor = StatsProcessor(dataset)
        for column, stats in processor.summarize(["MinTemp", "MaxTemp", "Rainfall"]):
            print(column)
            for name, value in stats.items():
                print(f"  {name}: {value}")
    except (OSError, KeyError, ValueError) as error:
        logger.error("Program stopped: %s", error)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler("weatherstats.log"), logging.StreamHandler()],
    )
    main()
