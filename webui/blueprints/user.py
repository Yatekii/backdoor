from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import Blueprint


import helpers
import models
from webui.wrappers import check_session

blueprint = Blueprint('user', __name__, template_folder='templates')


@blueprint.route('/view', defaults={'id': '0'})
@blueprint.route('/view/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def view(sqlsession, id):
    id = int(id)
    active = 'users'

    user = None
    if id > 0:
        user = sqlsession.query(models.User).filter_by(id=int(id)).first()

    users = sqlsession.query(models.User).filter_by().order_by(models.User.name.asc()).all()
    return render_template(
        'user.html',
        active=active,
        date=helpers.today(),
        id=id,
        user=user,
        users=users,
        previous=dict(request.args.items(multi=False))
    )


@blueprint.route('/add', methods=['POST'])
@check_session()
def add():
    id, errors = models.User.add(
        username=request.form['add_user_username'].lower(),
        password=request.form['add_user_password'],
        level=request.form['add_user_level'],
        name=request.form['add_user_name'],
        email=request.form['add_user_email'],
        nethzid=request.form['add_user_nethzid']
    )

    if id:
        flash('New user was created successfully', 'success')
        return redirect(url_for('user.view', id=id))
    else:
        for e in errors:
            flash(e[1], 'danger')
        return redirect(url_for(
            'user.view',
            user_username=request.form['add_user_username'],
            user_password=request.form['add_user_password'],
            user_name=request.form['add_user_name'],
            user_level=request.form['add_user_level'],
            user_email=request.form['add_user_email'],
            user_nethzid=request.form['add_user_nethzid']
        ))



@blueprint.route('/change/', defaults={'id': '0'})
@blueprint.route('/change/<id>', methods=['POST', 'GET'])
@check_session()
def change(id):
    print(request.form)
    id = int(id)
    if id > 0:
        if 'change_user_password_validate' in request.form:
            id, errors = models.User.change(
                id,
                password=request.form['change_user_password'],
                password_validate=request.form['change_user_password_validate']
            )
            if errors:
                for error in errors:
                    flash(error[1], 'danger')
                return redirect(url_for('profile.password'))
            flash('The password has ben changed.', 'success')
            return redirect(url_for('profile.password'))
        else:
            id, errors = models.User.change(
                id,
                level=request.form['change_user_level'],
                name=request.form['change_user_name'],
                email=request.form['change_user_email'],
                nethzid=request.form['change_user_nethzid']
            )
            if errors:
                for error in errors:
                    flash(error[1], 'danger')
            flash('User #%d has been changed.' % id, 'success')
            return redirect(request.referrer)


@blueprint.route('/remove', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove(sqlsession):
    user = sqlsession.query(models.User).filter_by(id=request.form['user_id']).first()

    if user:
        sqlsession.delete(user)
        flash('User %s was removed successfully.' % user.name, 'success')

    else:
        flash('User with id %d was not found.' % request.form['user_id'], 'danger')

    return redirect(url_for('user.view'))