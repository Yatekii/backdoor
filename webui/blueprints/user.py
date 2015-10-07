"""

    NFC controlled door access.
    Copyright (C) 2015  Yatekii yatekii(at)yatekii.ch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""


from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import Blueprint


import helpers
import models
from webui.wrappers import check_session, check_rights
from webui.permission_flags import *

blueprint = Blueprint('user', __name__, template_folder='templates')


@blueprint.route('/view', defaults={'id': '0'})
@blueprint.route('/view/<id>/', methods=['POST', 'GET'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_USERS)
@helpers.handle_dbsession()
def view(sqlsession, id):
    id = int(id)
    active = 'users'
    user = None
    if id > 0:
        user = sqlsession.query(models.User).filter_by(id=int(id)).first()

    permissions = None
    if user:
        print('actual', user.level)
        print('needed', OVER_NINETHOUSAND)
        permissions = [
            user.level & CAN_LOGIN,
            user.level & MANIPULATE_USERS,
            user.level & MANIPULATE_TOKENS,
            user.level & MANIPULATE_DEVICES,
            user.level & OVER_NINETHOUSAND
        ]

    users = sqlsession.query(models.User).filter_by().order_by(models.User.name.asc()).all()
    return render_template(
        'user.html',
        active=active,
        date=helpers.today(),
        id=id,
        user=user,
        users=users,
        permissions=permissions,
        previous=dict(request.args.items(multi=False))
    )


@blueprint.route('/add', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_USERS)
def add():
    level = 0;
    permissions = {}
    for checkbox in request.form:
        if 'permission' in checkbox:
            print('split', checkbox.split('permission')[1])
            level |= 1 << int(checkbox.split('permission')[1])
            permissions[checkbox] = 1
    print('level', level)
    id, errors = models.User.add(
        username=request.form['add_user_username'].lower(),
        password=request.form['add_user_password'],
        level=level,
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
            user_email=request.form['add_user_email'],
            user_nethzid=request.form['add_user_nethzid'],
            **permissions
        ))



@blueprint.route('/change/', defaults={'id': '0'})
@blueprint.route('/change/<id>', methods=['POST', 'GET'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_USERS)
def change(id):
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
            else:
                flash('The password has ben changed.', 'success')
            return redirect(url_for('profile.password'))
        else:
            level = 0
            for checkbox in request.form:
                if 'permission' in checkbox:
                    print('split', checkbox.split('permission')[1])
                    level |= 1 << int(checkbox.split('permission')[1])
            print('level', level)
            id, errors = models.User.change(
                id,
                level=level,
                name=request.form['change_user_name'],
                email=request.form['change_user_email'],
                nethzid=request.form['change_user_nethzid']
            )
            if errors:
                for error in errors:
                    flash(error[1], 'danger')
            else:
                flash('User #%d has been changed.' % id, 'success')
            return redirect(request.referrer)


@blueprint.route('/remove', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_USERS)
@helpers.handle_dbsession()
def remove(sqlsession):
    user = sqlsession.query(models.User).filter_by(id=request.form['user_id']).first()

    if user:
        sqlsession.delete(user)
        flash('User %s was removed successfully.' % user.name, 'success')

    else:
        flash('User with id %d was not found.' % request.form['user_id'], 'danger')

    return redirect(url_for('user.view'))