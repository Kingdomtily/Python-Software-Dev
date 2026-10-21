import csv

'''grab all of the data from the csv and append it to weather_data'''
def load_csv(filename):
    weather_data = []
    with open(filename, mode = "r", encoding="utf-8") as file:
        content = csv.reader(file)
        for lines in content:
            weather_data.append(lines)

'''Take weather_data and write it to a new file'''
def write_csv(filename, data):
    with open(filename, mode = "w", encoding="utf-8") as file:
        for row in data:
            file.writelines(row)

if __name__ == "__main__":
    file_name = "WeatherData/Weather Training Data.csv"
    load_csv(file_name)
    print(len(weather_data))
    