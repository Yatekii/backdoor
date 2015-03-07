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

@app.route('/profile/', defaults={'category': 'general'})
@app.route('/profile/<category>', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def profile(sqlsession, category):
    active = 'profile'

    user = sqlsession.query(models.User).filter_by(username=session['username']).first()

    if category == 'password':
        return render_template(
            'profile_password.html',
            active=active,
            category=category,
            user=user
        )
    elif category == 'settings':
        devices = sqlsession.query(models.Device).all()
        return render_template(
            'profile_settings.html',
            active=active,
            category=category,
            user=user,
            devices=devices
        )
    elif category == 'tokens':
        return render_template(
            'profile_tokens.html',
            active=active,
            category=category,
            user=user
        )
    else:
        return render_template(
            'profile_general.html',
            active=active,
            category=category,
            user=user
        )