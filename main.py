'''Main is where we interact with all of the code in other files throughouth the program'''
from weatherstats import loader, stats

def main():
    '''Main function to include all of the program's instructions'''
    data = loader.load_csv("WeatherData/Weather Training Data.csv")
    loader.write_csv("output.csv", data)
    mintemp_mean = stats.calculate_mean(data, "MinTemp")
    print(mintemp_mean)


if __name__ == "__main__":
    main()
    