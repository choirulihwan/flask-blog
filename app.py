from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/hello/<name>/')
def hello(name):
    return render_template('index.html', name=name)


if __name__ == '__main__':
    app.debug = True
    app.run()
