import csv

weather_data = []

def load_csv(filename):
    with open(filename, mode = 'r') as file:
        content = csv.reader(file)
        for lines in content:
            weather_data.append(lines)

if __name__ == "__main__":
    file_name = "WeatherData/Weather Training Data.csv"
    load_csv(file_name)
    print(len(weather_data))
    