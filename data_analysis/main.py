import csv

def load_csv(filename):
    '''grab all of the data from the csv and append it to weather_data'''
    weather_data = []
    with open(filename, mode="r", encoding="utf-8") as file:
        content = csv.reader(file)
        for row in content:
            weather_data.append(row)
        return weather_data

def write_csv(filename, data):
    '''Take weather_data and write it to a new file'''
    with open(filename, mode="w", encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    file_name = "WeatherData/Weather Training Data.csv"
    data = load_csv(file_name)
    write_csv("output.csv", data)

    