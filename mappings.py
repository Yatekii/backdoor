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
import backdoor
import models


app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'adsjkfhasdjkfhjkasdhfkasdjhfkloajshdfjskdf'


def check_secret():
    def checker_helper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
                if contains_secret():
                    return f(*args, **kwargs)
                else:
                    abort(403)
        return inner
    return checker_helper


def contains_secret():
    return True
    return request.cookies.get('bastli_backdoor_shared_secret') == config.shared_secret


@app.route('/test')
def test():
    return backdoor.users_to_json_by_filter()


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Set Cookie')
    response.set_cookie('bastli_backdoor_shared_secret', 'VERYSECUREPASSPHRASE')
    return response


@app.route('/')
@check_secret()
def home():
    return redirect(url_for('list_users'))


@app.route('/json/<type>', methods=['GET'])
@check_secret()
def json(type):
    print(type)
    if type == 'users':
        return backdoor.users_to_json_by_filter()
    elif type == 'devices':
        return backdoor.devices_to_json_by_filter()
    abort(403)


@app.route('/overview')
@check_secret()
def overview():
    return redirect(url_for('list_users'))


################################### USERS ##############################################


@app.route('/list_users/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_users/<filter>/<value>/', methods=['POST', 'GET'])
@check_secret()
@backdoor.handle_dbsession()
def list_users(session, filter, value):
    active = 'list_users'
    if filter == 'default' or value == 'all':
        users = session.query(models.User).all()
    else:
        users = session.query(models.User).filter_by(**{filter: value}).all()
    return render_template('list_users.html', active=active, date=backdoor.today(), users=users, previous=dict(request.args.items(multi=False)))


@app.route('/add_user', methods=['POST'])
@check_secret()
def add_user():
    error = False

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['add_user_email']):
        error = True
        flash('Please enter a valid email address', 'danger')

    if int(request.form['add_user_level']) not in range(0, 999):
        error = True
        flash('Please enter a valid number between 0 and 999 as the userlevel.', 'danger')

    if not error:
        backdoor.create_user(creation_date=backdoor.today(), name=request.form['add_user_name'], level=int(request.form['add_user_level']), email=request.form['add_user_email'], nethzid=request.form['add_user_nethzid'])
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
def remove_user():
    backdoor.remove_user_by_filter(id=request.form['user_id'])
    flash('User was removed successfully', 'success')
    return redirect(url_for('list_users'))

@app.route('/change_user_level', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def change_user_level(session):
    error = False
    user = session.query(models.User).filter_by(id=request.form.get('change_user_id')).first()
    if not user:
        error = True
        flash('User does not exist. Check that you use valid parameters', 'danger')

    if int(request.form['change_user_level']) not in range(0, 999):
        error = True
        flash('Please enter a valid number between 0 and 999 as the userlevel.', 'danger')

    if not error:
        user.level = int(request.form['change_user_level'])
        session.add(user)
        session.commit()
        flash('User %s has now level %d.' % (user.name, user.level), 'success')
    return redirect(url_for('list_users'))

@app.route('/change_user_email', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def change_user_email(session):
    error = False
    user = session.query(models.User).filter_by(id=request.form.get('change_user_id')).first()
    if not user:
        error = True
        flash('User does not exist. Check that you use valid parameters', 'danger')

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
@backdoor.handle_dbsession()
def change_user_nethzid(session):
    error = False
    user = session.query(models.User).filter_by(id=request.form.get('change_user_id')).first()
    if not user:
        error = True
        flash('User does not exist. Check that you use valid parameters', 'danger')

    if not error:
        user.nethzid = request.form['change_user_nethzid']
        session.add(user)
        session.commit()
        flash('User %s has now nethzid %s.' % (user.name, user.nethzid), 'success')
    return redirect(url_for('list_users'))


######################################## TOKENS #############################################


@app.route('/list_tokens/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_tokens/<filter>/<value>/', methods=['POST', 'GET'])
@check_secret()
@backdoor.handle_dbsession()
def list_tokens(session, filter, value):
    active = 'list_tokens'
    if filter == 'default' or value == 'all':
        tokens = backdoor.list_tokens()
    else:
        tokens = backdoor.list_tokens(**{filter: value})
    session.add_all(tokens)
    return render_template('list_tokens.html', active=active, date=backdoor.today(), tokens=tokens, previous=dict(request.args.items(multi=False)))


@app.route('/add_token', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def add_token(session):

    owner = session.query(models.User).filter_by(id=request.form['add_token_owner_id']).first()

    error = False

    if not owner and request.form['add_token_owner'] != 'FREE':
        error = True
        flash('User does not exist. Please check your entry for owner!', 'danger')

    try:
        expiry_date = backdoor.str_to_date(request.form['add_token_expiry_date'])
    except BaseException:
        error = True
        flash('Expiry date has a bad format. Please check expiry date (Should be YYYY-mm-dd)!', 'danger')

    if not error:
        backdoor.create_token(
            value=backdoor.generate_token(),
            owner=owner,
            expiry_date=expiry_date,
            creation_date=backdoor.today()
        )
        flash('New token was created successfully', 'success')
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
def remove_token():
    backdoor.remove_token_by_filter(id=request.form['token_id'])
    flash('Token was removed successfully')
    return redirect(url_for('list_tokens'))


@app.route('/revoke_token', methods=['POST'])
@check_secret()
def revoke_token():
    if backdoor.revoke_token(request.form['token_id']):
        flash('Token was has successfully been revoked', 'success')
    else:
        flash('Revoking of Token failed. Are you sure that Token exists?', 'danger')
    return redirect(url_for('list_tokens'))


@app.route('/activate_token', methods=['POST'])
@check_secret()
def activate_token():
    expiry_date = backdoor.activate_token(request.form['token_id'])
    if expiry_date:
        flash('Token expiry date was has successfully been extended to %s' % expiry_date, 'success')
    else:
        flash('Token expiry date hasn\'t been modified. Could be due to broken config. Please contact an administrator.', 'danger')
    return redirect(url_for('list_tokens'))


@app.route('/change_token_owner', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def change_token_owner(session):
    error = False
    token = session.query(models.Token).filter_by(id=request.form.get('change_token_id')).first()
    if not token:
        error = True
        flash('Token does not exist. Check that you use valid parameters', 'danger')

    new_owner = session.query(models.User).filter_by(id=request.form.get('change_token_owner_id')).first()
    if not new_owner:
        error = True
        new_owner_query = session.query(models.User).filter_by(name=request.form.get('change_token_owner_name'))
        if new_owner_query.count() == 1:
            error = False
            new_owner = new_owner_query.first()

    if not new_owner and request.form.get('change_token_owner_name') != 'FREE':
        flash('User does not exist: %s' % new_owner, 'danger')

    if not error:
        token.owner = new_owner
        session.add(token)
        session.commit()
        flash('Token #%s has new owner %s.' % (token.id, token.owner.name), 'success')
    return redirect(url_for('list_tokens'))

@app.route('/change_token_expiry_date', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def change_token_expiry_date(session):
    error = False
    token = session.query(models.Token).filter_by(id=request.form.get('change_token_id')).first()
    if not token:
        error = True
        flash('Token does not exist. Check that you use valid parameters', 'danger')

    try:
        new_expiry_date = backdoor.str_to_date(request.form['change_token_expiry_date'])
    except BaseException:
        error = True
        flash('Expiry date has a bad format. Please check expiry date (Should be YYYY-mm-dd)!', 'danger')

    if not error:
        token.expiry_date = new_expiry_date
        session.add(token)
        session.commit()
        flash('Token #%s has expires %s.' % (token.id, token.expiry_date), 'success')
    return redirect(url_for('list_tokens'))


@app.route('/link_token_to_device', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def link_token_to_device(session):
    print(request.form)
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('link_token_device_id')).first()
    if not device:
        error = True
        flash('Device does not exist. Check that you use valid parameters', 'danger')

    token = session.query(models.Token).filter_by(id=request.form.get('link_token_id')).first()
    if not device:
        error = True
        flash('Token does not exist. Check that you use valid parameters', 'danger')

    if not error:
        device.tokens.append(token)
        session.add(device)
        session.commit()
        flash('Token #%s now available on device %s' % (token.id, device.name), 'success')
    return redirect(url_for('list_tokens'))


@app.route('/list_devices/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_devices/<filter>/<value>/', methods=['POST', 'GET'])
@check_secret()
@backdoor.handle_dbsession()
def list_devices(session, filter, value):
    active = 'list_devices'
    if filter == 'default' or value == 'all':
        devices = session.query(models.Device).all()
    else:
        devices = session.query(models.Device).filter_by(**{filter: value}).all()
    return render_template('list_devices.html', active=active, date=backdoor.today(), devices=devices, previous=dict(request.args.items(multi=False)))

@app.route('/add_device', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def add_device(session):
    error = False
    if not error:
        backdoor.create_device(
            name=request.form['add_device_name'],
            pubkey=request.form['add_device_pubkey'],
            creation_date=backdoor.today()
        )
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
def remove_device():
    backdoor.remove_device_by_filter(id=request.form['device_id'])
    flash('Device was removed successfully')
    return redirect(url_for('list_devices'))


@app.route('/change_device_name', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def change_device_name(session):
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()
    if not device:
        error = True
        flash('Device does not exist. Check that you use valid parameters', 'danger')

    if not error:
        device.name = request.form['change_device_name']
        session.add(device)
        session.commit()
        flash('Device #%s renamed to %s.' % (device.id, device.name), 'success')
    return redirect(url_for('list_devices'))


@app.route('/change_device_pubkey', methods=['POST'])
@check_secret()
@backdoor.handle_dbsession()
def change_device_pubkey(session):
    error = False
    device = session.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()
    if not device:
        error = True
        flash('Device does not exist. Check that you use valid parameters', 'danger')

    if not error:
        device.pubkey = request.form['change_device_pubkey']
        session.add(device)
        session.commit()
        flash('Device #%s has new pubkey.' % device.id, 'success')
    return redirect(url_for('list_devices'))


@app.route('/list_sounds/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_sounds/<filter>/<value>/', methods=['POST', 'GET'])
@check_secret()
@backdoor.handle_dbsession()
def list_sounds(session, filter, value):
    active = 'list_sounds'
    if filter == 'default' or value == 'all':
        tokens = backdoor.list_tokens()
    else:
        tokens = backdoor.list_tokens(**{filter: value})
    session.add_all(tokens)
    return render_template('list_tokens.html', active=active, date=backdoor.today(), tokens=tokens, previous=dict(request.args.items(multi=False)))


@app.route('/logs')
def logs():
    active = 'logs'
    return redirect(url_for('list_users'))