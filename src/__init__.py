from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
import uuid

#Creating and managing database

db = SQLAlchemy()
DB_NAME = "database.db"
    
#Message functionality (not implemented only if needed)
def saveMessage(msg, usersNum=0):
    from .models import Message
    message = Message(data=msg, user_id=current_user.id, encryption=5)
    print(message)
    
    db.session.add(message)
    db.session.commit()

def create_app():
    from .models import User
    from .views import views
    from .auth import auth

    app = Flask(__name__)
    app.config['SECRET_KEY'] = uuid.uuid4().hex
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
