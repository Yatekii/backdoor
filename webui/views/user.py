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


@app.route('/users/', defaults={'id': '0'})
@app.route('/users/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def users(sqlsession, id):
    id = int(id)
    active = 'users'

    user = None
    if id > 0:
        user = sqlsession.query(models.User).filter_by(id=int(id)).first()

    users = sqlsession.query(models.User).filter_by().order_by(models.User.name.asc()).all()

    return render_template(
        'users.html',
        active=active,
        date=helpers.today(),
        id=id,
        user=user,
        users=users,
        previous=dict(request.args.items(multi=False))
    )