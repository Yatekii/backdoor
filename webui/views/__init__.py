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

@app.route('/sounds/', defaults={'attribute': 'default', 'value': 'all'})
@app.route('/sounds/<attribute>/<value>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def sounds(sqlsession, attribute, value):
    active = 'sounds'
    return redirect(url_for('devices'))


@app.route('/logs')
@check_session()
def logs():
    active = 'logs'
    return redirect(url_for('users'))