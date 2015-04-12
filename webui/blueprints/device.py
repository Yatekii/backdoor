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

blueprint = Blueprint('device', __name__, template_folder='templates')


@blueprint.route('/view/', defaults={'id': '0'})
@blueprint.route('/view/<id>/', methods=['POST', 'GET'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def view(sqlsession, id):
    id = int(id)
    active = 'devices'
    device = None
    if id > 0:
        device = sqlsession.query(models.Device).filter_by(id=id).first()
    devices = sqlsession.query(models.Device).filter_by().all()

    return render_template(
        'device.html',
        active=active,
        date=helpers.today(),
        id=id,
        device=device,
        devices=devices,
        previous=dict(request.args.items(multi=False))
    )


@blueprint.route('/add', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def add(sqlsession):
    error = False

    if not error:
        device = models.Device(
            name=request.form['add_device_name'],
            pubkey=request.form['add_device_pubkey'],
            creation_date=helpers.today(),
            is_online=False,
            is_enabled=True
        )
        sqlsession.add(device)
        sqlsession.commit()
        flash('New device was created successfully', 'success')
        return redirect(url_for('device.view', id=device.id))

    else:
        return redirect(url_for(
            'device.view',
            device_name=request.form['add_device_name'],
            device_pubkey=request.form['add_device_pubkey']
        ))


@blueprint.route('/remove', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def remove(sqlsession):
    device = sqlsession.query(models.Device).filter_by(id=request.form['device_id']).first()

    if device:
        sqlsession.delete(device)
        flash('Device with id %s was successfully removed.' % request.form['device_id'], 'success')

    else:
        flash('Device with id %s was not found.' % request.form['device_id'], 'danger')

    return redirect(url_for('device.view'))


@blueprint.route('/change', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def change(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %s was not found.' % request.form['change_device_id'], 'danger')

    if device.is_online:
        error = True
        flash('Device with id %s is still online. Please make sure it\'s offline to make changes.'
              % request.form['change_device_id'], 'danger')

    if not error:
        device.name = request.form['change_device_name']
        device.pubkey = request.form['change_device_pubkey']
        flash('Device with id %d has been changed.' % device.id, 'success')

    return redirect(url_for('device.view', id=device.id))

@blueprint.route('/revoke', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def revoke(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=int(request.form.get('change_device_id'))).first()
    if not device:
        error = True
        flash('Device with id %s was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        error, errors = models.Device.revoke(device.id)
        if error:
            for e in errors:
                flash(e[1], 'danger')
        else:
            device.is_enabled = False
            flash('Device with id %d has been revoked.' % device.id, 'success')

    return redirect(url_for('device.view', id=device.id))

@blueprint.route('/enable', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def enable(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %s was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.is_enabled = True
        flash('Device with id %d has been enabled.' % device.id, 'success')

    return redirect(url_for('device.view', id=device.id))