import datetime
import functools
import re

from flask import Flask, flash
from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from flask import abort
from flask import make_response

import config
import helpers
import models


app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'adsjkfhasdjkfhjkasdhfkasdjhfkloajshdfjskdf'


def check_secret():
    def checker_helper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            request.cookies.get('bastli_backdoor_shared_secret') == config.shared_secret
            if True:
                return f(*args, **kwargs)
            else:
                abort(403)

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
    return redirect(url_for('list_users'))


@app.route('/json/<model>', methods=['GET'])
@check_secret()
def json(model):
    if model == 'users':
        return helpers.users_to_json_by_filter()
    elif model == 'devices':
        return helpers.devices_to_json_by_filter()
    abort(403)


# --------------------------------------------------    OVERVIEW    -------------------------------------------------- #


@app.route('/overview')
@check_secret()
def overview():
    return redirect(url_for('list_users'))


# --------------------------------------------------      USER      -------------------------------------------------- #


@app.route('/list_users/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_users/<attribute>/<value>/', methods=['POST', 'GET'])
@check_secret()
@helpers.handle_dbsession()
def list_users(session, attribute, value):
    active = 'list_users'

    if attribute == 'default' or value == 'all':
        users = session.query(models.User).all()
    else:
        users = session.query(models.User).filter_by(**{attribute: value}).all()

    return render_template(
        'list_users.html',
        active=active,
        date=helpers.today(),
        users=users,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/add_user', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def add_user(session):
    error = False

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['add_user_email']):
        error = True
        flash('Please enter a valid email address', 'danger')

    if int(request.form['add_user_level']) not in range(0, 999):
        error = True
        flash('Please enter a valid number between 0 and 999 as the userlevel.', 'danger')

    if not error:
        user = models.User(
            creation_date=helpers.today(),
            name=request.form['add_user_name'],
            level=int(request.form['add_user_level']),
            email=request.form['add_user_email'],
            nethzid=request.form['add_user_nethzid']
        )
        session.add(user)
        flash('New user was created successfully', 'success')
        return redirect(url_for('list_users'))

    else:
        return redirect(url_for(
            'list_users',
            user_name=request.form['add_user_name'],
            user_level=request.form['add_user_level'],
            user_email=request.form['add_user_email'],
            user_nethzid=request.form['add_user_nethzid']
        ))


@app.route('/remove_user', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def remove_user(session):
    user = session.query(models.User).filter_by(id=request.form['user_id']).first()

    if user:
        session.delete(user)
        flash('User %s was removed successfully.' % user.name, 'success')

    else:
        flash('User with id %d was not found.' % request.form['user_id'], 'danger')

    return redirect(url_for('list_users'))


@app.route('/change_user_level', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def change_user_level(session):
    error = False
    user = session.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if int(request.form['change_user_level']) not in range(0, 999):
        error = True
        flash('Please enter a valid number between 0 and 999 as the userlevel.', 'danger')

    if not error:
        user.level = int(request.form['change_user_level'])
        session.add(user)
        session.commit()
        flash('User %s is now level %d.' % (user.name, user.level), 'success')

    return redirect(url_for('list_users'))


@app.route('/change_user_email', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def change_user_email(session):
    error = False
    user = session.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['change_user_email']):
        error = True
        flash('Please enter a valid email address.', 'danger')

    if not error:
        user.email = request.form['change_user_email']
        session.add(user)
        session.commit()
        flash('User %s has now email %s.' % (user.name, user.email), 'success')

    return redirect(url_for('list_users'))


@app.route('/change_user_nethzid', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def change_user_nethzid(session):
    error = False
    user = session.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if not error:
        user.nethzid = request.form['change_user_nethzid']
        session.add(user)
        session.commit()
        flash('User %s has now nethzid %s.' % (user.name, user.nethzid), 'success')

    return redirect(url_for('list_users'))


# --------------------------------------------------     TOKENS     -------------------------------------------------- #


@app.route('/list_tokens/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_tokens/<attribute>/<value>/', methods=['POST', 'GET'])
@check_secret()
@helpers.handle_dbsession()
def list_tokens(session, attribute, value):
    active = 'list_tokens'

    if attribute == 'default' or value == 'all':
        tokens = session.query(models.Token).all()
    else:
        tokens = session.query(models.Token).filter_by(**{attribute: value}).all()

    return render_template(
        'list_tokens.html',
        active=active,
        date=helpers.today(),
        tokens=tokens,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/add_token', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def add_token(session):
    error = False
    owner = session.query(models.User).filter_by(id=request.form['add_token_owner_id']).first()

    if not owner:
        error = True
        owner_query = session.query(models.User).filter_by(name=request.form['add_token_owner_id'])
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
        session.add(token)
        flash('New token was successfully created.', 'success')
        return redirect(url_for('list_tokens'))

    else:
        return redirect(url_for(
            'list_tokens',
            token_owner_id=request.form['add_token_owner_id'],
            token_owner=request.form['add_token_owner'],
            token_expiry_date=request.form['add_token_expiry_date']
        ))


@app.route('/remove_token', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def remove_token(session):
    token = session.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        session.delete(token)
        flash('Token with id %d was removed successfully.' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('list_tokens'))


@app.route('/revoke_token', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def revoke_token(session):
    token = session.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        token.expiry_date = helpers.today() - datetime.timedelta(days=1)
        flash('Token with id %d was has successfully been revoked' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('list_tokens'))


@app.route('/activate_token', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def activate_token(session):
    error = True
    token = session.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        for date in config.semester_end:
            if date <= helpers.today():
                continue
            token.expiry_date = date
            error = False
            flash('Token expiry date was has successfully been extended to %s' % date, 'success')
            break

    if error:
        flash('Token expiry date hasn\'t been modified. Please contact an administrator.', 'danger')

    return redirect(url_for('list_tokens'))


@app.route('/change_token_expiry_date', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def change_token_expiry_date(session):
    error = False
    token = session.query(models.Token).filter_by(id=request.form.get('change_token_id')).first()

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

    return redirect(url_for('list_tokens'))


@app.route('/link_token_to_device', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def link_token_to_device(session):
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('link_token_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['link_token_device_id'], 'danger')

    token = session.query(models.Token).filter_by(id=request.form.get('link_token_id')).first()
    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['link_token_id'], 'danger')

    if not error:
        device.tokens.append(token)
        flash('Token with id %d now available on device %s' % (token.id, device.name), 'success')

    return redirect(url_for('list_tokens'))


@app.route('/remove_link_token_to_device', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def remove_link_token_to_device(session):
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('remove_link_token_to_device_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['link_token_device_id'], 'danger')

    token = session.query(models.Token).filter_by(id=request.form.get('remove_link_token_to_device_token_id')).first()
    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['link_token_id'], 'danger')

    if not error:
        device.tokens.remove(token)
        flash('Token with id %d has no longer access on device %s' % (token.id, device.name), 'success')

    return redirect(url_for('list_tokens'))


# --------------------------------------------------     DEVICE     -------------------------------------------------- #


@app.route('/list_devices/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_devices/<attribute>/<value>/', methods=['POST', 'GET'])
@check_secret()
@helpers.handle_dbsession()
def list_devices(session, attribute, value):
    active = 'list_devices'

    if attribute == 'default' or value == 'all':
        devices = session.query(models.Device).all()
    else:
        devices = session.query(models.Device).filter_by(**{attribute: value}).all()

    return render_template(
        'list_devices.html',
        active=active,
        date=helpers.today(),
        devices=devices,
        previous=dict(request.args.items(multi=False))
    )


@app.route('/add_device', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def add_device(session):
    error = False

    if not error:
        device = models.Device(
            name=request.form['add_device_name'],
            pubkey=request.form['add_device_pubkey'],
            creation_date=helpers.today()
        )
        session.add(device)
        flash('New device was created successfully', 'success')
        return redirect(url_for('list_devices'))

    else:
        return redirect(url_for(
            'list_devices',
            device_name=request.form['add_device_name'],
            device_pubkey=request.form['add_device_pubkey']
        ))


@app.route('/remove_device', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def remove_device(session):
    device = session.query(models.Device).filter_by(id=request.form['device_id']).first()

    if device:
        session.delete(device)
        flash('Device with id %d was successfully removed.' % request.form['device_id'])

    else:
        flash('Device with id %d was not found.' % request.form['device_id'], 'danger')

    return redirect(url_for('list_devices'))


@app.route('/change_device_name', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def change_device_name(session):
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.name = request.form['change_device_name']
        flash('Device with id %d renamed to %s.' % (device.id, device.name), 'success')

    return redirect(url_for('list_devices'))


@app.route('/change_device_pubkey', methods=['POST'])
@check_secret()
@helpers.handle_dbsession()
def change_device_pubkey(session):
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.pubkey = request.form['change_device_pubkey']
        flash('Device with id %d has new pubkey.' % device.id, 'success')

    return redirect(url_for('list_devices'))


@app.route('/list_sounds/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/list_sounds/<attribute>/<value>/', methods=['POST', 'GET'])
@check_secret()
@helpers.handle_dbsession()
def list_sounds(session, attribute, value):
    active = 'list_sounds'
    return redirect(url_for('list_devices'))


@app.route('/logs')
def logs():
    active = 'logs'
    return redirect(url_for('list_users'))