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

@app.route('/open/', defaults={'id' : '0'})
@app.route('/open/<id>', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def open(sqlsession, id):
    id = int(id)
    user = sqlsession.query(models.User).filter_by(username=session['username']).first()
    device = None
    if id == 0:
        if user.default_device:
            device = user.default_device
        else:
            id = int(config.config('default_door_device'))
    if id > 0 and not device:
        device = sqlsession.query(models.Device).filter_by(id=id).first()

    if device:
        access_granted = False

        if user.level > 9000:
            access_granted = True
        else:
            for token in user.tokens:
                if token in device.tokens:
                    access_granted = True
        if not access_granted:
            flash('No access on device with id %s' % id, 'danger')
        else:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((config.api_host, config.api_port))
                temporary_token = helpers.generate_token()
                q = Query()
                q.create_register_webui(config.webui_token, temporary_token)
                s.send(q.to_command())
                q.create_open(temporary_token, device.pubkey)
                s.send(q.to_command())
                q.create_unregister(temporary_token)
                s.send(q.to_command())
                s.close()
                flash('%s has been opened.' % device.name, 'success')
            except Exception as e:
                flash('Failed to access device %s' % device.name, 'danger')
    else:
        flash('Could not find device with id %s' % id, 'danger')
    return redirect(request.referrer)