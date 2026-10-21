import module1

if __name__ == "__main__":
    print("This is the main entry point of the program.")

    data = module1.load_csv("WeatherData/Weather Test Data.csv")
    module1.write_csv("Test File", data)

    