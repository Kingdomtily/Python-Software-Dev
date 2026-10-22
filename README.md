# Weather Data Analysis Project

This project is designed to interact with CSVs and read/write to files.

# What Does it do?

Loads csv files and can write them to other files, condense multiple to a single file, and can retrieve statistics about the files loaded.

# Functions

## load_csv()
`load_csv()` takes one parameter, *filename* and opens that file. It then returns that file in the form of a DataFrame. 
## write_csv()
`write_csv()` takes two parameters, *filename* and *data*. The filename is the destination that the program is writing to, while data is the information that is being written there. Currently the filename is set to `output.csv`.
## file_concat()
`file_concat()` utilizes pandas to take 2 different DataFrames and condense them into a single DataFrame. It then returns that DataFrame.

## def calculate_mean(data, column):
Calculate mean is passed a dataset, and a column name, and will calculate the mean of the numbers in that column. Then returns
that value.

## calculate_median(data, column):
Calculate median is passed a dataset, and a column name, and will calculate the median of the numbers in that column. Then returns that value.

## calculate_mode(data, column):
Calculate mode is passed a dataset, and a column name, and will calculate the mode of the numbers in that column. Then returns
that value. One thing to note is that it will always return the lowest value if two numbers have the same amount.

## calculate_range(data, column):
Calculate range is passed a dataset, and a column name, and will calculate the range of the numbers in that column. Then returns
that value.
# Dataset

Weather Test Data.csv, and Weather Training Data.csv. this is the Australia weather data from Kaggle [Kaggle](https://www.kaggle.com/datasets/arunavakrchakraborty/australia-weather-data)

# Built with

Python 3.14.7
windows 11
VS Code
[GitHub](www.github.com/kingdomtily)

# Prerequisites

Python 3
csv
pandas

## Installation
The package is published at: https://test.pypi.org/project/weatherstats-kingdomtily/
Create a virtual environment
activate it with windows powerhsell
install the package `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ weatherstats-kingdomtily`

# Usage
`python main.py` With current parameters it produces:
mean: 12.186399728729267 
mode: 9.6 
median: 12.0 
range: 42.4 
row count: 142193