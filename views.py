from course import app
from flask import render_template, redirect, url_for
from forms import IndexForm

@app.route('/', methods=['GET','POST'])
def hello_world():
    form = IndexForm()
    if form.validate_on_submit():#TODO: test for password
        return redirect(url_for('test', password=form.data))

    return render_template('index.html', form = form)


@app.route('/test', methods=['GET','POST'])
@app.route('/test/', methods=['GET','POST'])
def test():
    print '===='
    return render_template('test.html')