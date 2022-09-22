import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config:
    JSON_SORT_KEYS = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'GB24i29egei@#%@#'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 0) or 10
