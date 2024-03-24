class BaseConfig:
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = "do-i-really-need-this"
    FLASK_SECRET = SECRET_KEY
    DB_URL = "sqlite:///contracts.db"
