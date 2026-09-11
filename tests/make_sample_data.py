"""
Generates a small SYNTHETIC weatherAUS-like CSV purely so we can verify
main.py / weatherstats end-to-end before the real Kaggle dataset is
dropped into data/weatherAUS.csv. Not part of the package itself, and
not a substitute for the real 100k+ record dataset required by the
assignment.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 2000

locations = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"]
dates = pd.date_range("2015-01-01", periods=n, freq="D")

df = pd.DataFrame({
    "Date": dates,
    "Location": rng.choice(locations, size=n),
    "MinTemp": rng.normal(14, 5, n).round(1),
    "MaxTemp": rng.normal(23, 6, n).round(1),
    "Rainfall": np.abs(rng.exponential(2, n)).round(1),
    "Humidity9am": rng.integers(30, 100, n),
    "Humidity3pm": rng.integers(20, 90, n),
    "Pressure9am": rng.normal(1015, 5, n).round(1),
    "Pressure3pm": rng.normal(1012, 5, n).round(1),
    "WindSpeed9am": rng.integers(0, 40, n),
    "WindSpeed3pm": rng.integers(0, 45, n),
    "Temp9am": rng.normal(17, 5, n).round(1),
    "Temp3pm": rng.normal(21, 6, n).round(1),
    "RainToday": rng.choice(["Yes", "No"], size=n, p=[0.3, 0.7]),
    "RainTomorrow": rng.choice(["Yes", "No"], size=n, p=[0.3, 0.7]),
})

out_path = "data/weatherAUS_sample.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df):,} synthetic rows to {out_path}")
