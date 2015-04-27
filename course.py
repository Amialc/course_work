from flask import Flask
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)
app.config.from_object('config')
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)

login_serializer = Serializer(app.config['SECRET_KEY'], expires_in=60)

db = SQLAlchemy(app)

mail = Mail(app)

lm = LoginManager()
lm.init_app(app)

from views import *

if __name__ == '__main__':
    app.run(host='0.0.0.0')
