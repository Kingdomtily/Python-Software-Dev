from flask import Flask, render_template, request
from pyspark.sql import SparkSession, functions as F
from weatherstats.data_sources import CombinedCsvSource
from weatherstats.dataset import WeatherDataset
from weatherstats.processors import StatsProcessor
from weatherstats.charts import WeatherCharts
from weatherstats.models import db, Search

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
db.init_app(app)
with app.app_context():
    db.create_all()

spark = SparkSession.builder.appName("WeatherStats").master("local[*]").getOrCreate()
source = CombinedCsvSource(spark, ["WeatherData/Weather Training Data.csv", "WeatherData/Weather Test Data.csv"])
dataset = WeatherDataset(source.fetch().cache())
processor = StatsProcessor(dataset)
locations = sorted(row.Location for row in dataset.data.select("Location").distinct().collect())

@app.route("/")
def index():
    return render_template("index.html", locations=locations)

@app.route("/results", methods=["POST"])
def results():
    location = request.form["location"]
    column = request.form["column"]
    subset = StatsProcessor(WeatherDataset(dataset.data.filter(F.col("Location") == location)))
    _, stats = next(subset.summarize([column]))
    search = Search(location=location, column=column, mean=stats["mean"], median=stats["median"],
                    mode=stats["mode"], value_range=stats["range"])
    db.session.add(search)
    db.session.commit()
    return render_template("results.html", search=search)

@app.route("/history")
def history():
    searches = Search.query.order_by(Search.created.desc()).all()
    return render_template("history.html", searches=searches)

@app.route("/charts")
def charts():
    maker = WeatherCharts(processor, folder="static/charts")
    paths = [maker.rainfall_by_location(), maker.max_temp_histogram(), maker.humidity_rain_vs_dry()]
    return render_template("charts.html", charts=[p.name for p in paths])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)