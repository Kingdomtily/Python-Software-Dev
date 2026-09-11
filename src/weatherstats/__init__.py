"""
weatherstats
============

A small, installable package for loading the Kaggle "Rain in Australia"
weather dataset with pandas and computing descriptive statistics on it.

This package exists to demonstrate *modularization*: the loading logic,
the statistics logic, and the reporting logic each live in their own
module, and are re-exported here so that consumers can simply do::

    import weatherstats as ws

    df = ws.load_weather_data("data/weatherAUS.csv")
    stats_table = ws.descriptive_stats(df)
    report_text, _ = ws.generate_summary_report(df)
    print(report_text)

exactly the way you would use any other installed third-party library
(pandas, numpy, etc.) after ``pip install -e .``.
"""

from .data_loader import load_weather_data, load_and_combine_weather_data
from .stats import descriptive_stats
from .report import generate_summary_report

__all__ = [
    "load_weather_data",
    "load_and_combine_weather_data",
    "descriptive_stats",
    "generate_summary_report",
]

__version__ = "0.1.0"
