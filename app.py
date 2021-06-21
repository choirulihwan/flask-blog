from flask import Flask, render_template
#from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager
from flaskext.mysql import MySQL
from env import *


#db = SQLAlchemy()
#login_manager = LoginManager()
app = Flask(__name__)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = db_user
app.config['MYSQL_DATABASE_PASSWORD'] = db_password
app.config['MYSQL_DATABASE_DB'] = db_name
app.config['MYSQL_DATABASE_HOST'] = db_host
mysql.init_app(app)
conn = mysql.connect()

# filter
@app.template_filter('formatdatetime')
def format_datetime(value, format="%d %b %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    return value.strftime(format)

# function2
def convert_to_dict(result, cursor):
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in result:
        insertObject.append(dict(zip(columnNames, record)))
    return insertObject


# routing
@app.route('/')
def hello_world():
    cursor = conn.cursor()
    query = ("SELECT post_title, post_content, post_slug, nama_kategori, post_date "
             "FROM ci_posts a "
             "JOIN ci_categories b ON a.post_category = b.id_kategori")

    cursor.execute(query)
    result = cursor.fetchall()
    result_set = convert_to_dict(result, cursor)
    judul = 'Terbaru'
    return render_template('index.html', data=result_set, judul=judul)


@app.route('/<slug>/')
def single(slug):
    cursor = conn.cursor()
    query = ("SELECT a.post_title, a.post_content, a.post_date, b.nama, c.nama_kategori, c.slug, b.username "
             "FROM ci_posts a "
             "JOIN ci_users b ON a.post_author = b.id_user "
             "JOIN ci_categories c ON a.post_category = c.id_kategori "
             "WHERE post_slug = %s")
    cursor.execute(query, (slug))
    result = cursor.fetchone()
    return render_template('single.html', article=result)


@app.route('/cat/<slug>/')
def cat(slug):
    cursor = conn.cursor()
    query = ("SELECT post_title, post_content, post_slug, nama_kategori, post_date "
             "FROM ci_posts a "
             "JOIN ci_categories b ON a.post_category = b.id_kategori "
             "WHERE b.slug = %s")
    cursor.execute(query, (slug))
    result = cursor.fetchall()
    result_set = convert_to_dict(result, cursor)
    judul = 'Kategori ' + result_set[0]['nama_kategori']
    return render_template('index.html', data=result_set, judul=judul)


@app.route('/author/<name>/')
def author(name):
    cursor = conn.cursor()
    query = ("SELECT post_title, post_content, post_slug, nama_kategori, post_date, c.nama "
             "FROM ci_posts a "            
             "JOIN ci_categories b ON a.post_category = b.id_kategori "
             "JOIN ci_users c ON a.post_author = c.id_user "
             "WHERE c.username = %s")
    cursor.execute(query, (name))
    result = cursor.fetchall()
    result_set = convert_to_dict(result, cursor)
    judul = result_set[0]['nama']

    return render_template('index.html', data=result_set, judul=judul)


if __name__ == '__main__':
    app.debug = True
    app.run()
