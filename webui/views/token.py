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


@app.route('/tokens/', defaults={'id': '0'})
@app.route('/tokens/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def tokens(sqlsession, id):
    id = int(id)
    active = 'tokens'
    tokens = sqlsession.query(models.Token).filter_by().all()
    token = sqlsession.query(models.Token).filter_by(id=id).first()

    return render_template(
        'tokens.html',
        active=active,
        date=helpers.today(),
        id=id,
        token=token,
        tokens=tokens,
        previous=dict(request.args.items(multi=False))
    )