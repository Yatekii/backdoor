from flask import Flask, flash

from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from flask import abort
from flask import make_response

import config
import backdoor
import models


app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'adsjkfhasdjkfhjkasdhfkasdjhfkloajshdfjskdf'


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
    return redirect(url_for('list_users'))


@app.route('/list_users', methods=['POST', 'GET'])
def list_users():
    if contains_secret():
        return render_template('list_users.html', users=backdoor.list_users())
    else:
        abort(403)


@app.route('/add_user', methods=['POST'])
def add_user():
    if contains_secret():
        backdoor.create_user(name=request.form['name'], level=request.form['level'])
        flash('New user was created successfully')
        return redirect(url_for('list_users'))
    else:
        abort(403)


@app.route('/remove_user', methods=['GET'])
def remove_user():
    if contains_secret():
        backdoor.remove_user_by_filter(id=request.args['id'])
        flash('User was removed successfully')
        return redirect(url_for('list_users'))
    else:
        abort(403)

@app.route('/list_tokens', methods=['POST', 'GET'])
@backdoor.handle_dbsession()
def list_tokens(session):
    if contains_secret():
        tokens = backdoor.list_tokens()
        session.add_all(tokens)
        return render_template('list_tokens.html', tokens=tokens)
    else:
        abort(403)


@app.route('/add_token', methods=['POST'])
@backdoor.handle_dbsession()
def add_token(session):
    if contains_secret():
        owner = session.query(models.User).filter_by(id=request.form['owner']).first()
        if not owner:
            flash('User does not exist. Canceled creation of token')
            return redirect(url_for('list_tokens'))
        backdoor.create_token(value=request.form['value'], owner=owner, expiry_date=backdoor.str_to_date(request.form['expiry_date']), creation_date=backdoor.today())
        flash('New token was created successfully')
        return redirect(url_for('list_tokens'))
    else:
        abort(403)


@app.route('/remove_token', methods=['GET'])
def remove_token():
    if contains_secret():
        backdoor.remove_token_by_filter(id=request.args['id'])
        flash('Token was removed successfully')
        return redirect(url_for('list_tokens'))
    else:
        abort(403)


@app.route('/deactivate_token', methods=['GET'])
def deactivate_token():
    if contains_secret():
        backdoor.deactivate_token(request.args['id'])
        flash('Token was deactivated successfully')
        return redirect(url_for('list_tokens'))
    else:
        abort(403)

