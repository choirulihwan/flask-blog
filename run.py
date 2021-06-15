from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/hello/<name>/')
def hello(name):
    return 'Hello %s!' % name


if __name__ == '__main__':
    app.debug = True
    app.run()
