'''Main is where we interact with all of the code in other files throughouth the program'''
from weatherstats import loader

def main():
    '''Main function to include all of the program's instructions'''
    data = loader.load_csv("WeatherData/Weather Training Data.csv")
    loader.write_csv("output.csv", data)

if __name__ == "__main__":
    main()
    