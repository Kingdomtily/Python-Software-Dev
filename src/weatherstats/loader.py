'''This file is intended to be used as the main way to get data and write data to/from csv's, now updated to pandas.'''
import pandas as pd

def load_csv(filename):
    '''Gets data from filename and returns it'''
    data = pd.read_csv(filename)
    return data

def write_csv(filename, data):
    '''Writes data to a file specified with filename'''
    output_data = pd.DataFrame(data)
    output_data.to_csv(filename, index=False)

def file_concat(data1, data2):
    """Condenses the two loaded csvs into one, a bigger dataset to use"""
    return pd.concat([data1,data2], ignore_index=True)