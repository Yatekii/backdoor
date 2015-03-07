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

@app.route('/change_profile_settings', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_profile_settings(sqlsession):
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

    return redirect(url_for('profile', category='settings'))