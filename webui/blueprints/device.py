from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request


from flask import Blueprint


import helpers
import models
from webui.wrappers import check_session

blueprint = Blueprint('device', __name__, template_folder='templates')


@blueprint.route('/view/', defaults={'id': '0'})
@blueprint.route('/view/<id>/', methods=['POST', 'GET'])
@check_session()
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
@helpers.handle_dbsession()
def add(sqlsession):
    error = False

    if not error:
        device = models.Device(
            name=request.form['add_device_name'],
            pubkey=request.form['add_device_pubkey'],
            creation_date=helpers.today()
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
@helpers.handle_dbsession()
def change(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.name = request.form['change_device_name']
        device.pubkey = request.form['change_device_pubkey']
        flash('Device with id %d has been changed.' % device.id, 'success')

    return redirect(url_for('device.view', id=device.id))