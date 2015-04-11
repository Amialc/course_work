from course import app
from flask import render_template
from forms import IndexForm

@app.route('/')
def hello_world():
    form = IndexForm()
    return render_template('index.html', form = form)


@app.route('/test', methods=['GET','POST'])
@app.route('/test/', methods=['GET','POST'])
def test(password=''):
    print '====',password
    return render_template('test.html')