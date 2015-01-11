from flask import Flask, flash

from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from flask import abort
from flask import make_response

import config
import backdoor


app = Flask(__name__)
app.static_folder = '~/static'
app.secret_key = 'adsjkfhasdjkfhjkasdhfkasdjhfklöajshdfjskdf'


def contains_secret():
    return request.cookies.get('bastli_backdoor_shared_secret') == config.shared_secret


def is_get():
    return request.method == 'GET'


@app.route('/test')
def test():
    return app.static_folder


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Set Cookie')
    response.set_cookie('bastli_backdoor_shared_secret', 'VERYSECUREPASSPHRASE')
    return response


@app.route('/')
def home():
    return redirect(url_for('list_user'))


@app.route('/list_user', methods=['POST', 'GET'])
def list_user():
    if contains_secret():
        return render_template('list_user.html', users=backdoor.list_user())
    else:
        abort(403)


@app.route('/add_user', methods=['POST'])
def add_user():
    if contains_secret():
        backdoor.create_user(name=request.form['name'], level=request.form['level'])
        flash('New user was created successfully')
        return redirect(url_for('list_user'))
    else:
        abort(403)

@app.route('/remove_user', methods=['GET'])
def remove_user():
    if contains_secret():
        backdoor.remove_user_by_filter(id=request.args['id'])
        flash('User was removed successfully')
        return redirect(url_for('list_user'))
    else:
        abort(403)

