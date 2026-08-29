import csv

weather_data = []

def load_csv(filename):
    '''
    Use csv to open and read from the csv file
    appends to weather_data
    '''
    with open(filename, mode = 'r') as file:
        content = csv.reader(file)
        for lines in content:
            weather_data.append(lines)

if __name__ == "__main__":
    '''
    Currently loads the csv file and prints the length
    '''
    file_name = "/home/KingdomTily/GitHub/Python Software Dev/WeatherData/Weather Training Data.csv"
    load_csv(file_name)
    print(len(weather_data))
    