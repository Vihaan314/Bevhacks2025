from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import uuid

#Creating and managing database

db = SQLAlchemy()
DB_NAME = "database.db"
    
def create_app():
    from .views import views

    app = Flask(__name__)
    app.config['SECRET_KEY'] = uuid.uuid4().hex
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')

    with app.app_context():
        db.create_all()



    return app
