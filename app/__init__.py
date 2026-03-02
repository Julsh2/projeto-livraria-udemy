from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import login_manager
from .extensions import db, csrf, login
from .config import Config



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)
    login.init_app(app)

    with app.app_context():
        from . import routes, models
        db.create_all()

    @login.user_loader #configuração da segurança do login. 
    #meu usuário acesse outras telas apenas com login
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    return app