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
from flask import session
from flask import Blueprint


import helpers
import models
from webui.wrappers import check_session


blueprint = Blueprint('profile', __name__, template_folder='templates')


@blueprint.route('/general', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def general(sqlsession):
    active = 'profile'

    user = sqlsession.query(models.User).filter_by(username=session['username']).first()

    return render_template(
        'profile_general.html',
        active=active,
        category='general',
        user=user
    )

@blueprint.route('/password', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def password(sqlsession):
    active = 'profile'

    user = sqlsession.query(models.User).filter_by(username=session['username']).first()

    return render_template(
        'profile_password.html',
        active=active,
        category='password',
        user=user
    )


@blueprint.route('/settings', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def settings(sqlsession):
    active = 'profile'

    user = sqlsession.query(models.User).filter_by(username=session['username']).first()

    devices = sqlsession.query(models.Device).all()

    return render_template(
        'profile_settings.html',
        active=active,
        category='settings',
        user=user,
        devices=devices
    )


@blueprint.route('/tokens', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def tokens(sqlsession):
    active = 'profile'

    user = sqlsession.query(models.User).filter_by(username=session['username']).first()

    return render_template(
        'profile_tokens.html',
        active=active,
        category='tokens',
        user=user,
        date=helpers.today()
    )


@blueprint.route('/change_settings', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_settings(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_user_device_id')).first()

    if not device:
        # if 0 != int(request.form.get('change_user_device_id')):
        #     device = None
        error = True
        flash('Device with id %s was not found.' % request.form.get('change_user_device_id'), 'danger')

    if not error:
        user.default_device = device
        flash('User %s has been changed.' % (user.name), 'success')

    return redirect(url_for('profile.settings'))