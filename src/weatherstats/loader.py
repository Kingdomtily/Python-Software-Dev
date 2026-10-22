import pandas as pd

def load_csv(filename):
    data = pd.read_csv(filename)
    return data