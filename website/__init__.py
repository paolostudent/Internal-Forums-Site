import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "database.db"

UPLOAD_FOLDER = 'website/static/uploads'

def create_app():
    app = Flask(__name__, static_url_path='/static')
    app.config['SECRET_KEY'] = "*MD?Xh;Ts0)=2s5"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Import and register blueprints
    from .views import views
    from .auth import auth
    from .forums import forums
    
    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(forums)
    
    # Import models
    from .models import User, Note, Post, Forum, Comment
    
    with app.app_context():
        db.create_all()
    
    # Configure login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app
