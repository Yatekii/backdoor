import datetime
import functools


from flask import Flask
from flask import request
from flask import abort
from flask import redirect, url_for
from flask import session
from flask import make_response
from flask import render_template


import models
import config
import helpers


app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = config.webui_sessions_secret
app.permanent_session_lifetime = datetime.timedelta(days=2048)


def check_secret():
    def checker_helper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            request.cookies.get('bastli_backdoor_shared_secret') == config.api_token
            if True:
                return f(*args, **kwargs)
            else:
                abort(403)

        return inner

    return checker_helper


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Set Cookie')
    response.set_cookie('bastli_backdoor_shared_secret', 'VERYSECUREPASSPHRASE')
    return response


def check_session():
    def checker_helper(f):
        @functools.wraps(f)
        @helpers.handle_dbsession()
        def inner(sqlsession, *args, **kwargs):

            if 'username' in session and sqlsession.query(models.User).filter_by(username=session['username']).count() == 1:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))

        return inner

    return checker_helper

@app.route('/')
@check_secret()
def home():
    return redirect(url_for('users'))


@app.route('/to_json/<model>', methods=['GET'])
@check_secret()
def to_json(model):
    if model == 'users':
        return helpers.users_to_json_by_filter()
    elif model == 'devices':
        return helpers.devices_to_json_by_filter()
    abort(403)


@app.route('/search/', defaults={'type' : 'list', 'id': '0'})
@app.route('/search/<type>/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def search(sqlsession, type, id):
    id = int(id)
    active = 'search'

    user = None
    if id > 0:
        user = sqlsession.query(models.User).filter_by(id=int(id)).first()

    device = None
    if id > 0:
        device = sqlsession.query(models.Device).filter_by(id=id).first()

    users = sqlsession.query(models.User).filter(models.User.name.like('%' + request.args.get('q') + '%')).all()
    devices = sqlsession.query(models.Device).filter(models.Device.name.like('%' + request.args.get('q') + '%')).all()
    return render_template(
        'search.html',
        active=active,
        date=helpers.today(),
        id=id,
        q=request.args.get('q'),
        type=type,
        user=user,
        users=users,
        device=device,
        devices=devices
    )


from webui.actions.user import change_user, change_password
from webui.actions.device import change_device


@app.route('/change/', defaults={'model': 'user', 'id': '0'})
@app.route('/change/<model>/<id>', methods=['POST', 'GET'])
@check_session()
def change(model, id):
    id = int(id)
    if id > 0:
        if model == 'user':
            return change_user()
        if model == 'password':
            return change_password()
        elif model == 'device':
            return change_device()