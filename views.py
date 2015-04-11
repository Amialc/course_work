from course import app
from flask import render_template

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/test', methods=['GET','POST'])
@app.route('/test/', methods=['GET','POST'])
def test(password=''):
    print '====',password
    return render_template('test.html')