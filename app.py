from flask import Flask, render_template, request
from flaskext.mysql import MySQL
from env import *
import math

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


def query_utama():
    query = ("SELECT a.post_title, a.post_content, a.post_date, b.nama, c.nama_kategori, c.slug, b.username, "
             "a.post_slug, a.post_id "
             "FROM ci_posts a "
             "JOIN ci_users b ON a.post_author = b.id_user "
             "JOIN ci_categories c ON a.post_category = c.id_kategori ")
    return query


def query_order():
    query = ("order by a.post_date desc limit %s, %s")
    return query


def query_categories():
    query = ("select * from ci_categories")
    return query


def get_categories():
    cursor = conn.cursor()
    query = query_categories()
    cursor.execute(query)
    result = cursor.fetchall()
    categories = convert_to_dict(result, cursor)
    return categories


def get_recent_posts():
    cursor = conn.cursor()
    query = (query_utama() + query_order())
    cursor.execute(query, (0, jml_recent_posts))
    result = cursor.fetchall()
    recent_posts = convert_to_dict(result, cursor)
    return recent_posts


def get_related_posts(cat_slug, slug):
    cursor = conn.cursor()
    query = (query_utama() +
              " where c.slug = %s " +
              " and a.post_slug != %s " +
              query_order())
    cursor.execute(query, (cat_slug, slug, 0, jml_related_posts))
    # print(cursor._last_executed)
    result = cursor.fetchall()
    related_posts = convert_to_dict(result, cursor)

    return related_posts


def get_next_post(post_id):
    cursor = conn.cursor()
    query = (query_utama() +
              " where a.post_id = (select min(post_id) from ci_posts where post_id > %s) ")
    cursor.execute(query, (post_id))
    result = cursor.fetchone()
    if result is not None:
        return result
    else:
        return []


def get_previous_post(post_id):
    cursor = conn.cursor()
    query = (query_utama() +
              " where a.post_id = (select max(post_id) from ci_posts where post_id < %s) ")
    cursor.execute(query, (post_id))
    result = cursor.fetchone()
    # print(result)
    # print(cursor._last_executed)
    if result is not None:
        return result
    else:
        return []


# routing
@app.route('/')
@app.route('/page/<int:i>')
def index(i=1):
    start = (i * per_page) - (per_page)

    cursor = conn.cursor()

    query = query_utama()
    cursor.execute(query)
    jml = cursor.rowcount
    jml_page = int(math.ceil(jml/per_page))

    cursor2 = conn.cursor()
    query2 = (query + query_order())
    cursor2.execute(query2, (start, per_page))
    result2 = cursor2.fetchall()
    result_set = convert_to_dict(result2, cursor)

    judul = 'Terbaru'
    return render_template('index.html', data=result_set, judul=judul, jml_page=jml_page)


@app.route('/<slug>/')
def single(slug):
    cursor = conn.cursor()
    query = (query_utama() + "WHERE post_slug = %s")
    cursor.execute(query, (slug))
    result = cursor.fetchone()

    # categories
    categories = get_categories()

    # recent posts
    recent_posts = get_recent_posts()

    # related posts
    related_posts = get_related_posts(result[5], result[7])

    # next post
    next_post = get_next_post(result[8])

    # previous post
    previous = get_previous_post(result[8])
    print(previous)

    return render_template('single.html', article=result, categories=categories, recent_posts=recent_posts,
                           related_posts=related_posts, previous=previous, next=next_post)


@app.route('/<jenis>/<name>/')
@app.route('/<jenis>/<name>/page/<int:i>')
def archive(jenis, name, i=1):
    start = (i * per_page) - (per_page)

    cursor = conn.cursor()
    if jenis == 'cat':
        query = (query_utama() + "WHERE c.slug = %s")
    elif jenis == 'author':
        query = (query_utama() + "WHERE b.username = %s")

    cursor.execute(query, (name))

    jml = cursor.rowcount
    jml_page = int(math.ceil(jml / per_page))

    cursor2 = conn.cursor()
    query2 = (query + query_order())
    cursor2.execute(query2, (name, start, per_page))
    result2 = cursor2.fetchall()
    result_set = convert_to_dict(result2, cursor)

    if jenis == 'cat':
        if len(result_set) > 0:
            judul = 'Kategori ' + result_set[0]['nama_kategori']
        else:
            judul = 'Kategori ' + request.path.split("/")[2]
    elif jenis == 'author':
        if len(result_set) > 0:
            judul = result_set[0]['nama']
        else:
            judul = request.path.split("/")[2]

    return render_template('archive.html', data=result_set, judul=judul, jml_page=jml_page)


if __name__ == '__main__':
    app.debug = True
    app.run()
