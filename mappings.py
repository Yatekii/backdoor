from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import redirect

import config
import backdoor


app = Flask(__name__)


def contains_secret():
    return 'shared_secret' in request.args and request.args['shared_secret'] == config.shared_secret


def is_get():
    return request.method == 'GET'


@app.route('/')
def home():
    return redirect(url_for('list_user'))


@app.route('/list_user', methods=['GET'])
def list_user():
    if is_get() and contains_secret():
        return render_template('list_user.html', secret=request.args['shared_secret'], data=backdoor.list_user())
    else:
        return render_template('access_denied.html')


@app.route('/add_user', methods=['GET'])
def add_user():
    if is_get() and contains_secret():
        print('Test')
    else:
        return render_template('access_denied.html')

