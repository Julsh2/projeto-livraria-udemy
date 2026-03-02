from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


db = SQLAlchemy()
csrf = CSRFProtect()
login = LoginManager()
login.login_view = 'login'