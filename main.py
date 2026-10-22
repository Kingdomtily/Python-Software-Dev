'''Main is where we interact with all of the code in other files throughouth the program'''
from weatherstats import loader, stats

def main():
    '''Main function to include all of the program's instructions'''
    dataset1 = loader.load_csv("WeatherData/Weather Training Data.csv")
    dataset2 = loader.load_csv("WeatherData/Weather Test Data.csv")
    data = loader.file_concat(dataset1,dataset2)
    loader.write_csv("output.csv", data)
    mintemp_mean = stats.calculate_mean(data, "MinTemp")
    mintemp_mode = stats.calculate_mode(data, "MinTemp")
    mintemp_median = stats.calculate_median(data, "MinTemp")
    mintemp_range = stats.calculate_range(data,"MinTemp")
    num_rows = len(data)
    
    print(f"mean: {mintemp_mean} \nmode: {mintemp_mode} \nmedian: {mintemp_median} \nrange: {mintemp_range} \nrow count: {num_rows}")


if __name__ == "__main__":
    main()
    