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


@app.route('/settings/', defaults={'category' : 'general'})
@app.route('/settings/<category>', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def settings(sqlsession, category):
    active = 'settings'

    if category == 'readonly':
        return render_template(
            'settings_readonly.html',
            active=active,
            category=category,
            webui_token=config.webui_token,
            server_token=config.server_token,
            api_token=config.api_token
        )
    elif category == 'general':
        devices = sqlsession.query(models.Device).all()
        return render_template(
            'settings_general.html',
            active=active,
            category=category,
            flash_device=config.config('flash_device'),
            default_door_device=config.config('default_door_device'),
            devices=devices,
            semester_end_dates=config.config('semester_end_dates')
        )
    else:
        devices = sqlsession.query(models.Device).all()
        return render_template(
            'settings_general.html',
            active=active,
            category=category,
            flash_device=config.config('flash_device'),
            default_door_device=config.config('default_door_device'),
            devices=devices,
            semester_end_dates=config.config('semester_end_dates')
        )