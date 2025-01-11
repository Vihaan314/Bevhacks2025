from src import db
from sqlalchemy.sql import func

class Message(db.Model):
    latitude = db.Column(db.Numeric(precision = 17, scale = 14), nullable = False)
    longitude = db.Column(db.Numeric(precision = 17, scale = 14), nullable = False)

    description = db.Column(db.String())

    date = db.Column(db.DateTime(timezone=True), default=func.now())
