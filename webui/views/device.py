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


@app.route('/devices/', defaults={'id': '0'})
@app.route('/devices/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def devices(sqlsession, id):
    id = int(id)
    active = 'devices'
    device = None
    if id > 0:
        device = sqlsession.query(models.Device).filter_by(id=id).first()
    devices = sqlsession.query(models.Device).filter_by().all()

    return render_template(
        'devices.html',
        active=active,
        date=helpers.today(),
        id=id,
        device=device,
        devices=devices,
        previous=dict(request.args.items(multi=False))
    )