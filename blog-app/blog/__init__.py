from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask import redirect, flash
import nltk

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'BLOG_SECRET_KEY'

    """
    -------- Create USER and DATABASE ---------

    # mysql
    mysql > CREATE USER 'ssdi'@'localhost' IDENTIFIED BY 'ssdi';
    mysql > GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES, RELOAD on *.* TO 'ssdi'@'localhost' WITH GRANT OPTION;
    mysql > FLUSH PRIVILEGES;
    mysql > exit;

    # mysql -u ssdi -p
    mysql > CREATE DATABASE blog;

    """

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ssdi:ssdi@localhost/blog'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    nltk.download('stopwords')


    from .blogRoutes import blogRoutes
    from .userRoutes import userRoutes

    app.register_blueprint(blogRoutes, url_prefix="/")
    app.register_blueprint(userRoutes, url_prefix="/")
    
    @app.errorhandler(404)
    def not_found(e):
        flash(str(e), category='error')
        return redirect('/')

    from .models import User

    with app.app_context():
        from .models import User  # Import routes
        db.create_all()  # Create sql tables for our data models


    login_manager = LoginManager()
    login_manager.login_view = "userRoutes.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))



    return app
