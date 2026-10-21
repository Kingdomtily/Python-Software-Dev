# Weather Data Analysis Project

This project is designed to interact with CSVs and read/write to files.

# What Does it do?

Currently this only loads `Weather Training Data.csv` and writes that content to `output.csv`

# Functions

## load_csv()
`load_csv()` takes one parameter, *filename* and opens that file. It loads all of the data inside to a list called `weather_data`. It then returns that value. Currently it is only set up to take "Weather test data.csv", in the future it may be possible to be an input for the user to enter.
## write_csv()
`write_csv()` takes two parameters, *filename* and *data*. The filename is the destination that the program is writing to, while data is the information that is being written there. Currently the filename is set to `output.csv`.

# Dataset

Weather Test Data.csv, this is the Australia weather data from Kaggle [Kaggle](https://www.kaggle.com/datasets/arunavakrchakraborty/australia-weather-data)

# Built with

Python 3.14.7

# Prerequisites

Python 3
csv

# Usage

Currently only reads a file and writes to another file, maintaining the csv format.