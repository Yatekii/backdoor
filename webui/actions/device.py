import datetime
import functools
import re
import time
import json
import socket
import hashlib

from flask import Flask, flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import abort
from flask import make_response
from flask import stream_with_context, request, Response
from flask import session


import config
import helpers
import models
from query import Query
from webui import app
from webui import check_session


@app.route('/add_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def add_device(sqlsession):
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
        return redirect(url_for('devices', id=device.id))

    else:
        return redirect(url_for(
            'devices',
            device_name=request.form['add_device_name'],
            device_pubkey=request.form['add_device_pubkey']
        ))


@app.route('/remove_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_device(sqlsession):
    device = sqlsession.query(models.Device).filter_by(id=request.form['device_id']).first()

    if device:
        sqlsession.delete(device)
        flash('Device with id %s was successfully removed.' % request.form['device_id'], 'success')

    else:
        flash('Device with id %s was not found.' % request.form['device_id'], 'danger')

    return redirect(url_for('devices'))


@helpers.handle_dbsession()
def change_device(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('change_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['change_device_id'], 'danger')

    if not error:
        device.name = request.form['change_device_name']
        device.pubkey = request.form['change_device_pubkey']
        flash('Device with id %d has been changed.' % device.id, 'success')

    return redirect(url_for('devices', id=device.id))