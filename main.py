'''Main is where we interact with all of the code in other files throughouth the program'''
from weatherstats.data_sources import CombinedCsvSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import StatsProcessor

def main():
    '''Main function to include all of the program's instructions'''
    source = CombinedCsvSource(["WeatherData/Weather Training Data.csv", "WeatherData/Weather Test Data.csv"])
    dataset = WeatherDataset.from_source(source)
    dataset.save("output.csv")
    print(dataset)

    processor = StatsProcessor(dataset)
    mintemp_mean = processor.calculate_mean("MinTemp")
    mintemp_mode = processor.calculate_mode("MinTemp")
    mintemp_median = processor.calculate_median("MinTemp")
    mintemp_range = processor.calculate_range("MinTemp")

    print(f"mean: {mintemp_mean} \nmode: {mintemp_mode} \nmedian: {mintemp_median} \nrange: {mintemp_range}")


if __name__ == "__main__":
    main()
