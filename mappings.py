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


def contains_secret():
    return True
    return request.cookies.get('bastli_backdoor_shared_secret') == config.shared_secret


def is_get():
    return request.method == 'GET'


@app.route('/test')
def test():
    return backdoor.users_to_json_by_filter()


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Set Cookie')
    response.set_cookie('bastli_backdoor_shared_secret', 'VERYSECUREPASSPHRASE')
    return response


@app.route('/')
def home():
    return redirect(url_for('list_users'))


@app.route('/json/<type>', methods=['GET'])
def json(type):
    print(type)
    if type == 'users':
        return backdoor.users_to_json_by_filter()
    abort(403)


@app.route('/overview')
def overview():
    return redirect(url_for('list_users'))


@app.route('/list_users', methods=['POST', 'GET'])
@backdoor.handle_dbsession()
def list_users(session):
    if contains_secret():
        for key in active.keys():
            active[key] = ''
        active['users'] = menu_activator
        users = backdoor.list_users()
        session.add_all(users)
        return render_template('list_users.html', active=active, users=users)
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


@app.route('/list_tokens/', defaults={'filter': 'default', 'value': 'all'})
@app.route('/list_tokens/<filter>/<value>/', methods=['POST', 'GET'])
@backdoor.handle_dbsession()
def list_tokens(session, filter, value):
    print(filter)
    if contains_secret():
        if filter == 'default' or value == 'all':
            tokens = backdoor.list_tokens()
        else:
            tokens = backdoor.list_tokens(**{filter: value})
        session.add_all(tokens)
        for key in active.keys():
            active[key] = ''
        active['tokens'] = menu_activator
        return render_template('list_tokens.html', active=active, date=backdoor.today(), tokens=tokens, previous=dict(request.args.items(multi=False)))
    else:
        abort(403)


@app.route('/add_token', methods=['POST'])
@backdoor.handle_dbsession()
def add_token(session):
    if contains_secret():

        owner = session.query(models.User).filter_by(id=request.form['token_owner_id']).first()

        if not owner and request.form['token_owner'] != 'FREE':
            flash('User does not exist. Please check your entry for owner!', 'danger')
            return redirect(url_for(
                'list_tokens',
                token_owner_id=request.form['token_owner_id'],
                token_owner=request.form['token_owner'],
                token_creation_date=backdoor.today(),
                token_expiry_date=request.form['token_expiry_date']
            ))

        if backdoor.today() != backdoor.str_to_date(request.form['token_creation_date']):
            flash('Creation date was adjusted. Please give your OK!', 'info')
            return redirect(url_for(
                'list_tokens',
                token_owner_id=request.form['token_owner_id'],
                token_owner=request.form['token_owner'],
                token_creation_date=backdoor.today(),
                token_expiry_date=request.form['token_expiry_date']
            ))

        try:
            expiry_date = backdoor.str_to_date(request.form['token_expiry_date'])
        except BaseException:
            flash('Expiry date has a bad format. Please check expiry date (Should be YYYY-mm-dd)!', 'danger')
            return redirect(url_for(
                'list_tokens',
                token_owner_id=request.form['token_owner_id'],
                token_owner=request.form['token_owner'],
                token_creation_date=backdoor.today(),
                token_expiry_date=request.form['token_expiry_date']
            ))

        backdoor.create_token(
            value=backdoor.generate_token(),
            owner=owner,
            expiry_date=expiry_date,
            creation_date=backdoor.today()
        )

        flash('New token was created successfully', 'success')
        return redirect(url_for('list_tokens'))
    else:
        abort(403)


@app.route('/remove_token', methods=['POST'])
def remove_token():
    if contains_secret():
        backdoor.remove_token_by_filter(id=request.form['id'])
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


@app.route('/logs')
def logs():
    return redirect(url_for('list_users'))