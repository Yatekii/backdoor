import datetime
import functools
import re
import time
import json
import socket
import hashlib

from flask import Flask, flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import abort
from flask import make_response
from flask import stream_with_context, request, Response
from flask import session


import config
import helpers
import models
from query import Query


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


@app.route('/test')
def test():
    return helpers.users_to_json_by_filter()


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Set Cookie')
    response.set_cookie('bastli_backdoor_shared_secret', 'VERYSECUREPASSPHRASE')
    return response


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


# --------------------------------------------------      LOGIN     -------------------------------------------------- #


@app.route('/login', methods=['GET', 'POST'])
@helpers.handle_dbsession()
def login(sqlsession):
    if request.method == 'POST':
        password = hashlib.sha256(request.form['password'].encode('utf-8'))
        user = sqlsession.query(models.User).filter_by(username=request.form['username'].lower(), password=password.hexdigest()).first()
        if 'failed_attempts' not in session:
            session['failed_attempts'] = 0
        if user and user.level > 9000:
            session['username'] = user.username
            session.permanent = True
            session.pop('failed_attempts', None)
            return redirect(url_for('profile'))
        flash('Wrong password, username or permission.', 'danger')
        session['failed_attempts'] = int(session['failed_attempts']) + 1
        return render_template('login.html', username=request.form['username'])
    if 'username' in session:
        return redirect(url_for('profile'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# --------------------------------------------------     PROFILE    -------------------------------------------------- #


@app.route('/open/', defaults={'id' : '0'})
@app.route('/open/<id>', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def open(sqlsession, id):
    id = int(id)
    if id == 0:
        id = int(config.config('default_door_device'))
    if id > 0:
        device = sqlsession.query(models.Device).filter_by(id=id).first()
        if device:
            user = sqlsession.query(models.User).filter_by(username=session['username']).first()
            access_granted = False

            if user.level > 9000:
                access_granted = True
            else:
                for token in user.tokens:
                    if token in device.tokens:
                        access_granted = True
            if not access_granted:
                flash('No access on device with id %s' % id, 'danger')
            else:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((config.api_host, config.api_port))
                    temporary_token = helpers.generate_token()
                    q = Query()
                    q.create_register_webui(config.webui_token, temporary_token)
                    s.send(q.to_command())
                    q.create_open(temporary_token, device.pubkey)
                    s.send(q.to_command())
                    q.create_unregister(temporary_token)
                    s.send(q.to_command())
                    s.close()
                    flash('%s has been opened.' % device.name, 'success')
                except Exception as e:
                    flash('Failed to access device %s' % device.name, 'danger')
        else:
            flash('Could not find device with id %s' % id, 'danger')
    else:
        flash('Could not find device with id %s' % id, 'danger')
    return redirect(request.referrer)


# --------------------------------------------------     PROFILE    -------------------------------------------------- #


@app.route('/profile')
@check_session()
@helpers.handle_dbsession()
def profile(sqlsession):
    active = 'profile'
    user = sqlsession.query(models.User).filter_by(username=session['username']).first()
    return render_template('profile.html', active=active, user=user)


# --------------------------------------------------    SETTINGS    -------------------------------------------------- #


@app.route('/settings/', defaults={'category' : 'list'})
@app.route('/settings/<category>', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def settings(sqlsession, category):
    active = 'settings'

    if category == 'readonly':
        return render_template(
            'settings_readonly.html',
            active=active,
            webui_token=config.webui_token,
            server_token=config.server_token,
            api_token=config.api_token
        )
    elif category == 'general':
        devices = sqlsession.query(models.Device).all()
        return render_template(
            'settings_general.html',
            active=active,
            flash_device=config.config('flash_device'),
            default_door_device=config.config('default_door_device'),
            devices=devices,
            semester_end_dates=config.config('semester_end_dates')
        )
    else:
        devices = sqlsession.query(models.Device).all()
        return render_template(
            'settings_general.html',
            active=active,
            flash_device=config.config('flash_device'),
            default_door_device=config.config('default_door_device'),
            devices=devices,
            semester_end_dates=config.config('semester_end_dates')
        )


@app.route('/change_general_settings', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_general_settings(sqlsession):
    error = False

    config.store_config('flash_device', request.form['change_flash_device'])
    config.store_config('default_door_device', request.form['change_default_door_device'])

    dates = []
    for key in request.form:
        if 'change_semester_end_date_' in key:
            try:
                print(request.form[key])
                dates.append(helpers.date_to_str(helpers.str_to_date(request.form[key])))
            except BaseException:
                error = True
                flash('At least one date has a bad format. It should be YYYY-mm-dd!', 'danger')
                break
    if not error:
        sorted_dates = sorted(dates, key=lambda date: helpers.str_to_date(date))
        config.store_config('semester_end_dates', sorted_dates)

    flash('New settings have successfully been stored.', 'success')
    return redirect(url_for('settings'))


# --------------------------------------------------     SEARCH     -------------------------------------------------- #

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


# --------------------------------------------------      USER      -------------------------------------------------- #

@app.route('/users/', defaults={'id': '0'})
@app.route('/users/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def users(sqlsession, id):
    id = int(id)
    active = 'users'

    user = None
    if id > 0:
        user = sqlsession.query(models.User).filter_by(id=int(id)).first()

    users = sqlsession.query(models.User).filter_by().order_by(models.User.name.asc()).all()

    return render_template(
        'users.html',
        active=active,
        date=helpers.today(),
        id=id,
        user=user,
        users=users,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/list_users/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_users/<attribute>/<value>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def list_users(sqlsession, attribute, value):
    active = 'list_users'

    if attribute == 'default' or value == 'all':
        users = sqlsession.query(models.User).all()
    else:
        users = sqlsession.query(models.User).filter_by(**{attribute: value}).all()

    return render_template(
        'list_users.html',
        active=active,
        date=helpers.today(),
        users=users,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/add_user', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def add_user(sqlsession):
    error = False

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['add_user_email']):
        error = True
        flash('Please enter a valid email address', 'danger')

    try:
        level = int(request.form['add_user_level'])
    except Exception:
        level = -1

    if request.form['add_user_level'] == 'over 9000' or request.form['add_user_level'] == '> 9000' or request.form['add_user_level'] == 'over ninethousand':
        level = 9999

    if level not in range(0, 10000):
        error = True
        flash('Please enter a valid number between 0 and 9999 as the userlevel.', 'danger')

    if sqlsession.query(models.User).filter_by(username=request.form['add_user_username'].lower()).first():
        error = True
        flash('That username exists yet. Please choose a different one.', 'danger')

    if not error:
        password = hashlib.sha256(request.form['add_user_password'].encode('utf-8'))
        user = models.User(
            creation_date=helpers.today(),
            username=request.form['add_user_username'].lower(),
            password=password.hexdigest(),
            name=request.form['add_user_name'],
            level=level,
            email=request.form['add_user_email'],
            nethzid=request.form['add_user_nethzid']
        )
        sqlsession.add(user)
        sqlsession.commit()
        flash('New user was created successfully', 'success')
        return redirect(url_for('users', id=user.id))

    else:
        return redirect(url_for(
            'users',
            user_username=request.form['add_user_username'],
            user_password=request.form['add_user_password'],
            user_name=request.form['add_user_name'],
            user_level=request.form['add_user_level'],
            user_email=request.form['add_user_email'],
            user_nethzid=request.form['add_user_nethzid']
        ))


@app.route('/remove_user', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_user(sqlsession):
    user = sqlsession.query(models.User).filter_by(id=request.form['user_id']).first()

    if user:
        sqlsession.delete(user)
        flash('User %s was removed successfully.' % user.name, 'success')

    else:
        flash('User with id %d was not found.' % request.form['user_id'], 'danger')

    return redirect(url_for('users'))


@helpers.handle_dbsession()
def change_user(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    try:
        level = int(request.form['change_user_level'])
    except Exception:
        level = -1

    if request.form['change_user_level'] == 'over 9000' or request.form['change_user_level'] == '> 9000' or request.form['change_user_level'] == 'over ninethousand':
        level = 999

    if level not in range(0, 10000):
        error = True
        flash('Please enter a valid number between 0 and 9999 as the userlevel.', 'danger')

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['change_user_email']):
        error = True
        flash('Please enter a valid email address.', 'danger')

    if not error:
        user.level = level
        user.name = request.form['change_user_name']
        user.email = request.form['change_user_email']
        user.nethzid = request.form['change_user_nethzid']
        flash('User %s has been changed.' % (user.name, user.nethzid), 'success')

    return redirect(url_for('users', id=user.id))


@app.route('/change/', defaults={'model': 'user', 'id': '0'})
@app.route('/change/<model>/<id>', methods=['POST', 'GET'])
@check_session()
def change(model, id):
    id = int(id)
    if id > 0:
        if model == 'user':
            return change_user()
        elif model == 'device':
            return change_device()


@app.route('/change_user_name', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_user_name(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if not error:
        user.name = request.form['change_user_name']
        flash('Your name has been changed to %s.' % user.name, 'success')

    return redirect(url_for('users', id=user.id))


@app.route('/change_user_password', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_user_password(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if request.form['change_user_password'] != request.form['change_user_password_validation']:
        error = True
        flash('The entered passwords do not match.', 'danger')

    if not error:
        password = hashlib.sha256(request.form['change_user_password'].encode('utf-8'))
        user.password = password.hexdigest()
        flash('The password has ben changed.', 'success')

    return redirect(url_for('profile'))


@app.route('/change_user_level', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_user_level(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    try:
        level = int(request.form['change_user_level'])
    except Exception:
        level = -1

    print(request.form['change_user_level'])
    if request.form['change_user_level'] == 'over 9000' or request.form['change_user_level'] == '> 9000' or request.form['change_user_level'] == 'over ninethousand':
        level = 9999
    print(level)

    if level not in range(0, 10000):
        error = True
        flash('Please enter a valid number between 0 and 9999 as the userlevel.', 'danger')

    if not error:
        user.level = level
        flash('User %s is now level %d.' % (user.name, user.level), 'success')

    return redirect(url_for('users', id=user.id))


@app.route('/change_user_email', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_user_email(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['change_user_email']):
        error = True
        flash('Please enter a valid email address.', 'danger')

    if not error:
        user.email = request.form['change_user_email']
        flash('User %s has now email %s.' % (user.name, user.email), 'success')

    return redirect(url_for('users', id=user.id))


@app.route('/change_user_nethzid', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_user_nethzid(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if not error:
        user.nethzid = request.form['change_user_nethzid']
        flash('User %s has now nethzid %s.' % (user.name, user.nethzid), 'success')

    return redirect(url_for('users', id=user.id))


# --------------------------------------------------     TOKENS     -------------------------------------------------- #


@app.route('/tokens/', defaults={'id': '0'})
@app.route('/tokens/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def tokens(sqlsession, id):
    id = int(id)
    active = 'tokens'
    tokens = sqlsession.query(models.Token).filter_by().all()
    token = sqlsession.query(models.Token).filter_by(id=id).first()

    return render_template(
        'tokens.html',
        active=active,
        date=helpers.today(),
        id=id,
        token=token,
        tokens=tokens,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/list_tokens/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_tokens/<attribute>/<value>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def list_tokens(sqlsession, attribute, value):
    active = 'list_tokens'

    if attribute == 'default' or value == 'all':
        tokens = sqlsession.query(models.Token).all()
    elif attribute == 'owner':
        owner = sqlsession.query(models.Token).filter_by(id=int(value)).first()
        if owner:
            tokens = sqlsession.query(models.Token).filter_by(owner=owner).all()
        else:
            tokens = []
    else:
        tokens = sqlsession.query(models.Token).filter_by(**{attribute: value}).all()

    return render_template(
        'list_tokens.html',
        active=active,
        date=helpers.today(),
        tokens=tokens,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/add_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def add_token(sqlsession):
    error = False
    owner = sqlsession.query(models.User).filter_by(id=request.form['add_token_owner_id']).first()

    if not owner:
        error = True
        owner_query = sqlsession.query(models.User).filter_by(name=request.form['add_token_owner'])
        if owner_query.count() == 1:
            error = False
            owner = owner_query.first()
        else:
            flash('User with id %s was not found.' % request.form.get('add_token_owner_id'), 'danger')

    expiry_date = helpers.today()
    try:
        expiry_date = helpers.str_to_date(request.form['add_token_expiry_date'])
    except BaseException:
        error = True
        flash('Expiry date has a bad format. It should be YYYY-mm-dd.', 'danger')

    if not error:
        token = models.Token(
            value=helpers.generate_token(),
            owner=owner,
            expiry_date=expiry_date,
            creation_date=helpers.today()
        )
        sqlsession.add(token)
        sqlsession.commit()
        flash('New token was successfully created.', 'success')
        return redirect(url_for('tokens', id=token.id))

    else:
        return redirect(url_for(
            'tokens',
            token_owner_id=request.form['add_token_owner_id'],
            token_owner=request.form['add_token_owner'],
            token_expiry_date=request.form['add_token_expiry_date']
        ))


@app.route('/remove_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_token(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        sqlsession.delete(token)
        flash('Token with id %d was removed successfully.' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('tokens'))


@app.route('/revoke_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def revoke_token(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        token.expiry_date = helpers.today() - datetime.timedelta(days=1)
        flash('Token with id %d was has successfully been revoked' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('tokens', id=token.id))


@app.route('/activate_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def activate_token(sqlsession):
    error = True
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    print(config.config('semester_end_dates'))

    if token:
        for date in config.config('semester_end_dates'):
            date = helpers.str_to_date(date)
            if date <= helpers.today():
                continue
            token.expiry_date = date
            error = False
            flash('Token expiry date was has successfully been extended to %s' % date, 'success')
            break

    if error:
        flash('Token expiry date hasn\'t been modified. Please contact an administrator.', 'danger')

    return redirect(url_for('tokens', id=token.id))


@app.route('/change_token_expiry_date', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_token_expiry_date(sqlsession):
    error = False
    token = sqlsession.query(models.Token).filter_by(id=request.form.get('change_token_id')).first()

    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['change_token_id'], 'danger')

    new_expiry_date = helpers.today()
    try:
        new_expiry_date = helpers.str_to_date(request.form['change_token_expiry_date'])
    except BaseException:
        error = True
        flash('Expiry date has a bad format. It should be YYYY-mm-dd!', 'danger')

    if not error:
        token.expiry_date = new_expiry_date
        flash('Token #%d expires on %s.' % (token.id, token.expiry_date), 'success')

    return redirect(url_for('tokens', id=token.id))


@app.route('/link_token_to_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def link_token_to_device(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('link_token_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['link_token_device_id'], 'danger')

    token = sqlsession.query(models.Token).filter_by(id=request.form.get('link_token_id')).first()
    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['link_token_id'], 'danger')

    if not error:
        device.tokens.append(token)
        flash('Token with id %d now available on device %s' % (token.id, device.name), 'success')

    return redirect(url_for('tokens', id=token.id))


@app.route('/remove_link_token_to_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_link_token_to_device(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('remove_link_token_to_device_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['link_token_device_id'], 'danger')

    token = sqlsession.query(models.Token).filter_by(id=request.form.get('remove_link_token_to_device_token_id')).first()
    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['link_token_id'], 'danger')

    if not error:
        device.tokens.remove(token)
        flash('Token with id %d has no longer access on device %s' % (token.id, device.name), 'success')

    return redirect(url_for('tokens', id=token.id))


@app.route('/token_flashed', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def token_flashed(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form.get('token_id')).first()

    if not token:
        return 'False'

    if token.flashed:
        return 'True'
    return 'False'


@app.route('/flash_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def flash_token(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form.get('token_id')).first()
    device = sqlsession.query(models.Device).filter_by(id=config.config('flash_device')).first()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.api_host, config.api_port))
    temporary_token = temporary_token = helpers.generate_token()
    q = Query()
    q.create_register_webui(config.webui_token, temporary_token)
    s.send(q.to_command())
    q.create_flash(temporary_token, token.value, device.pubkey)
    s.send(q.to_command())
    q.create_unregister(temporary_token)
    s.send(q.to_command())
    s.close()

    return redirect(url_for('tokens', id=token.id))


# --------------------------------------------------     DEVICE     -------------------------------------------------- #


@app.route('/devices/', defaults={'id': '0'})
@app.route('/devices/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def devices(sqlsession, id):
    id = int(id)
    active = 'devices'
    device = None
    if id > 0:
        device = sqlsession.query(models.Device).filter_by(id=id).first()
    devices = sqlsession.query(models.Device).filter_by().all()

    return render_template(
        'devices.html',
        active=active,
        date=helpers.today(),
        id=id,
        device=device,
        devices=devices,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/list_devices/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_devices/<attribute>/<value>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def list_devices(sqlsession, attribute, value):
    active = 'list_devices'

    if attribute == 'default' or value == 'all':
        devices = sqlsession.query(models.Device).all()
    else:
        devices = sqlsession.query(models.Device).filter_by(**{attribute: value}).all()

    return render_template(
        'list_devices.html',
        active=active,
        date=helpers.today(),
        devices=devices,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/add_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def add_device(sqlsession):
    error = False

    if not error:
        device = models.Device(
            name=request.form['add_device_name'],
            pubkey=request.form['add_device_pubkey'],
            creation_date=helpers.today()
        )
        sqlsession.add(device)
        sqlsession.commit()
        flash('New device was created successfully', 'success')
        return redirect(url_for('devices', id=device.id))

    else:
        return redirect(url_for(
            'devices',
            device_name=request.form['add_device_name'],
            device_pubkey=request.form['add_device_pubkey']
        ))


@app.route('/remove_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_device(sqlsession):
    device = sqlsession.query(models.Device).filter_by(id=request.form['device_id']).first()

    if device:
        sqlsession.delete(device)
        flash('Device with id %s was successfully removed.' % request.form['device_id'], 'success')

    else:
        flash('Device with id %s was not found.' % request.form['device_id'], 'danger')

    return redirect(url_for('devices'))


@helpers.handle_dbsession()
def change_device(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.name = request.form['change_device_name']
        device.pubkey = request.form['change_device_pubkey']
        flash('Device with id %d has been changed.' % device.id, 'success')

    return redirect(url_for('devices', id=device.id))


@app.route('/change_device_name', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_device_name(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.name = request.form['change_device_name']
        flash('Device with id %d renamed to %s.' % (device.id, device.name), 'success')

    return redirect(url_for('devices', id=device.id))


@app.route('/change_device_pubkey', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_device_pubkey(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.pubkey = request.form['change_device_pubkey']
        flash('Device with id %d has new pubkey.' % device.id, 'success')

    return redirect(url_for('devices', id=device.id))


@app.route('/sounds/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/sounds/<attribute>/<value>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def sounds(sqlsession, attribute, value):
    active = 'sounds'
    return redirect(url_for('devices'))


@app.route('/logs')
@check_session()
def logs():
    active = 'logs'
    return redirect(url_for('users'))


# --------------------------------------------------      API       -------------------------------------------------- #


def eventstream(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        def gen():
            for event, msg in f(*args, **kwargs):
                yield bytes('event: %s\r\ndata: %s\r\n\r\n' % (event, json.dumps(msg)), 'ascii')
        return Response(gen(), mimetype='text/event-stream', direct_passthrough=True)
    return wrapper


@app.route('/events')
@eventstream
def events():
    for x in range(10):
        yield 'time_event', x
        time.sleep(1.0)

@app.route('/stream', methods=['GET', 'POST'])
def streamed_response():
    def generate():
        yield 'Hello \n'
        time.sleep(5.0)
        yield 'swagga\n'
        time.sleep(5.0)
        yield '!\n'
    return Response(stream_with_context(generate()))