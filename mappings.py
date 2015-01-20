import functools


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
menu_activator = 'class=active'
active = {
    'overview': '',
    'users': '',
    'tokens': '',
    'logs': ''
}


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
    abort(403)


@app.route('/overview')
@check_secret()
def overview():
    return redirect(url_for('list_users'))


@app.route('/list_users/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_users/<filter>/<value>/', methods=['POST', 'GET'])
@check_secret()
@backdoor.handle_dbsession()
def list_users(session, filter, value):
    if filter == 'default' or value == 'all':
        users = session.query(models.User).all()
    else:
        users = session.query(models.User).filter_by(**{filter: value}).all()
    for key in active.keys():
        active[key] = ''
    active['users'] = menu_activator
    return render_template('list_users.html', active=active, users=users)


@app.route('/add_user', methods=['POST'])
@check_secret()
def add_user():
    backdoor.create_user(name=request.form['name'], level=request.form['level'])
    flash('New user was created successfully')
    return redirect(url_for('list_users'))


@app.route('/remove_user', methods=['GET'])
@check_secret()
def remove_user():
    backdoor.remove_user_by_filter(id=request.args['id'])
    flash('User was removed successfully')
    return redirect(url_for('list_users'))


@app.route('/list_tokens/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_tokens/<filter>/<value>/', methods=['POST', 'GET'])
@check_secret()
@backdoor.handle_dbsession()
def list_tokens(session, filter, value):
    if filter == 'default' or value == 'all':
        tokens = backdoor.list_tokens()
    else:
        tokens = backdoor.list_tokens(**{filter: value})
    session.add_all(tokens)
    for key in active.keys():
        active[key] = ''
    active['tokens'] = menu_activator
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

    if backdoor.today() != backdoor.str_to_date(request.form['add_token_creation_date']):
            error = True
            flash('Creation date was adjusted. Please give your OK!', 'info')

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
            token_creation_date=backdoor.today(),
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


@app.route('/logs')
def logs():
    return redirect(url_for('list_users'))