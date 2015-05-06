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

import datetime

from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import Blueprint

import config
import helpers
import models
from webui.wrappers import check_session, check_rights
from webui.permission_flags import *


blueprint = Blueprint('token', __name__, template_folder='templates')


@blueprint.route('/view', defaults={'id': '0'})
@blueprint.route('/view/<id>/', methods=['POST', 'GET'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def view(sqlsession, id):
    id = int(id)
    active = 'tokens'
    tokens = sqlsession.query(models.Token).filter_by().all()
    token = sqlsession.query(models.Token).filter_by(id=id).first()

    return render_template(
        'token.html',
        active=active,
        date=helpers.today(),
        id=id,
        token=token,
        tokens=tokens,
        previous=dict(request.args.items(multi=False))
    )


@blueprint.route('/add', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def add(sqlsession):
    id, errors = models.Token.add(
        owner=request.form['add_token_owner_id'],
        owner_name=request.form['add_token_owner'],
        expiry_date=request.form['add_token_expiry_date']
    )

    if id:
        flash('New token was successfully created.', 'success')
        return redirect(url_for('token.view', id=id))
    else:
        for e in errors:
            flash(e[1], 'danger')
        return redirect(url_for(
            'token.view',
            token_owner_id=request.form['add_token_owner_id'],
            token_owner_name=request.form['add_token_owner'],
            token_expiry_date=request.form['add_token_expiry_date']
        ))


@blueprint.route('/remove', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def remove(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        sqlsession.delete(token)
        flash('Token with id %d was removed successfully.' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('token.view'))


@blueprint.route('/revoke', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def revoke(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        token.expiry_date = helpers.today() - datetime.timedelta(days=1)
        flash('Token with id %d was has successfully been revoked' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(request.referrer)


@blueprint.route('/activate', methods=['POST'])
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@check_session()
def activate():
    date = models.Token.activate(int(request.form['token_id']))
    if date:
        flash('Token expiry date was has successfully been extended to %s' % helpers.date_to_str(date), 'success')
    else:
        flash('Token expiry date has not been modified. Please contact an administrator.', 'danger')

    return redirect(request.referrer)


@blueprint.route('/link_to_device', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def link_to_device(sqlsession):
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

    return redirect(url_for('token.view', id=token.id))


@blueprint.route('/remove_link_to_device', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def remove_link_to_device(sqlsession):
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

    return redirect(request.referrer)


@blueprint.route('/flashed', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def flashed(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form.get('token_id')).first()

    if not token:
        return 'False'

    if token.flashed:
        return 'True'
    return 'False'


@blueprint.route('/flash', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_TOKENS)
@helpers.handle_dbsession()
def flash_(sqlsession):
    error, errors = models.Token.flash(int(request.form.get('token_id')), int(config.read_config('flash_device')))
    if error:
        for e in errors:
            flash(e[1], 'danger')
    else:
        flash('Flashed token successfully.', 'success')
    return redirect(url_for('token.view', id=request.form.get('token_id')))