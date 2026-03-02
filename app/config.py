from dotenv import load_dotenv
load_dotenv()

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "the-dev-need-change-this")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False