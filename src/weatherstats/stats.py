'''This is the stats file, utilized to gather statistics from passed data.'''

def calculate_mean(data, column):
    '''Calculate mean is passed a dataset, and a column name, and will calculate the mean of the numbers in that column. Then returns
    that value.'''
    mean = data[column].mean()
    return mean


def calculate_median(data, column):
    '''Calculate median is passed a dataset, and a column name, and will calculate the median of the numbers in that column. Then returns
    that value.'''
    median = data[column].median()
    return median


def calculate_mode(data, column):
    '''Calculate mode is passed a dataset, and a column name, and will calculate the mode of the numbers in that column. Then returns
    that value. One thing
    to note is that it will always return the lowest value if two numbers have the same amount.'''
    mode = data[column].mode()
    return mode.iloc[0]


def calculate_range(data, column):
    '''Calculate range is passed a dataset, and a column name, and will calculate the range of the numbers in that column. Then returns
    that value.'''
    low_val = data[column].min()
    high_val = data[column].max()
    return high_val - low_val

