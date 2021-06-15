from flask import Flask, render_template
#from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager
from flaskext.mysql import MySQL

#db = SQLAlchemy()
#login_manager = LoginManager()

app = Flask(__name__)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'flask_blog'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()


@app.route('/')
def hello_world():
    cursor = conn.cursor()

    query = ("SELECT post_title, post_content FROM ci_posts");
    # "WHERE hire_date BETWEEN %s AND %s")
    # cursor.execute(query, (hire_start, hire_end))
    cursor.execute(query)
    return render_template('index.html', data=cursor)


# @app.route('/hello/<name>/')
# def hello(name):
#     return render_template('index.html', name=name)


if __name__ == '__main__':
    app.debug = True
    app.run()
