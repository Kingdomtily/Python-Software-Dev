"""Class for calculating statistics on a WeatherDataset."""

class StatsProcessor:
    """Calculates statistics on one column of a WeatherDataset."""
    def __init__(self, dataset):
        self.dataset = dataset

    def calculate_mean(self, column):
        return self.dataset.data[column].mean()

    def calculate_median(self, column):
        return self.dataset.data[column].median()

    def calculate_mode(self, column):
        """Returns the lowest value if there is a tie."""
        return self.dataset.data[column].mode().iloc[0]

    def calculate_range(self, column):
        return self.dataset.data[column].max() - self.dataset.data[column].min()
