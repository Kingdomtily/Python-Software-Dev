from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50))
    column = db.Column(db.String(50))
    mean = db.Column(db.Float)
    median = db.Column(db.Float)
    mode = db.Column(db.Float)
    value_range = db.Column(db.Float)
    created = db.Column(db.DateTime, default=datetime.now)