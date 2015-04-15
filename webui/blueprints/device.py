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
from sqlalchemy import and_


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
    s = sqlsession.query(models.Service).filter_by().all()
    services = []
    for service in s:
        services.append((service, device in service.devices))

    return render_template(
        'device.html',
        active=active,
        date=helpers.today(),
        id=id,
        device=device,
        devices=devices,
        services=services,
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


@blueprint.route('/change_service', methods=['POST'])
@check_session()
@check_rights(OVER_NINETHOUSAND | MANIPULATE_DEVICES)
@helpers.handle_dbsession()
def change_service(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('device_id')).first()
    service = sqlsession.query(models.Service).filter_by(id=request.form.get('service_id')).first()


    if not device:
        error = True
        flash('Device with id %s was not found.' % request.form['device_id'], 'danger')

    if not service:
        error = True
        flash('Service with id %s was not found.' % request.form['service_id'], 'danger')

    if not error:
        if request.form.get('add_service'):
            if service not in device.services:
                device.services.append(service)
                users = sqlsession.query(models.User).filter(
                    and_(
                        ~models.User.data.any(service=service),
                        models.User.tokens.any(models.Token.devices.any(models.Device.services.contains(service)))
                    )
                ).all()
                print(users)
                for user in users:
                    if user.data is None:
                        user.data = []
                    for field in service.fields:
                        user.data.append(models.ServiceData(key=field.key, user=user, device=device, service=service))
                flash('Service %s has been added to device %s.' % (service.name, device.name), 'success')
            else:
                flash('Service is already activated. No need to activate it.', 'danger')

        elif request.form.get('remove_service'):
            if service in device.services:
                device.services.remove(service)
                flash('Service %s has been removed from device %s.' % (service.name, device.name), 'success')
            else:
                flash('Service is not activated. No need to remove it.', 'danger')

        elif request.form.get('purge_service'):
            sqlsession.query(models.ServiceData).filter_by(service=service).delete()
            flash('Data for service %s has been purged.' % service.name, 'success')

    return redirect(url_for('device.view', id=device.id))