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


@app.route('/add_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def add_token(sqlsession):
    error = False
    owner = sqlsession.query(models.User).filter_by(id=request.form['add_token_owner_id']).first()

    if not owner:
        error = True
        owner_query = sqlsession.query(models.User).filter_by(name=request.form['add_token_owner'])
        if owner_query.count() == 1:
            error = False
            owner = owner_query.first()
        else:
            flash('User with id %s was not found.' % request.form.get('add_token_owner_id'), 'danger')

    expiry_date = helpers.today()
    try:
        expiry_date = helpers.str_to_date(request.form['add_token_expiry_date'])
    except BaseException:
        error = True
        flash('Expiry date has a bad format. It should be YYYY-mm-dd.', 'danger')

    if not error:
        token = models.Token(
            value=helpers.generate_token(),
            owner=owner,
            expiry_date=expiry_date,
            creation_date=helpers.today()
        )
        sqlsession.add(token)
        sqlsession.commit()
        flash('New token was successfully created.', 'success')
        return redirect(url_for('tokens', id=token.id))

    else:
        return redirect(url_for(
            'tokens',
            token_owner_id=request.form['add_token_owner_id'],
            token_owner=request.form['add_token_owner'],
            token_expiry_date=request.form['add_token_expiry_date']
        ))


@app.route('/remove_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_token(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        sqlsession.delete(token)
        flash('Token with id %d was removed successfully.' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('tokens'))


@app.route('/revoke_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def revoke_token(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    if token:
        token.expiry_date = helpers.today() - datetime.timedelta(days=1)
        flash('Token with id %d was has successfully been revoked' % token.id, 'success')

    else:
        flash('Token with id %d was not found.' % request.form['token_id'], 'danger')

    return redirect(url_for('tokens', id=token.id))


@app.route('/activate_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def activate_token(sqlsession):
    error = True
    token = sqlsession.query(models.Token).filter_by(id=request.form['token_id']).first()

    print(config.config('semester_end_dates'))

    if token:
        for date in config.config('semester_end_dates'):
            date = helpers.str_to_date(date)
            if date <= helpers.today():
                continue
            token.expiry_date = date
            error = False
            flash('Token expiry date was has successfully been extended to %s' % date, 'success')
            break

    if error:
        flash('Token expiry date hasn\'t been modified. Please contact an administrator.', 'danger')

    return redirect(url_for('tokens', id=token.id))


@app.route('/link_token_to_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def link_token_to_device(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('link_token_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['link_token_device_id'], 'danger')

    token = sqlsession.query(models.Token).filter_by(id=request.form.get('link_token_id')).first()
    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['link_token_id'], 'danger')

    if not error:
        device.tokens.append(token)
        flash('Token with id %d now available on device %s' % (token.id, device.name), 'success')

    return redirect(url_for('tokens', id=token.id))


@app.route('/remove_link_token_to_device', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_link_token_to_device(sqlsession):
    error = False
    device = sqlsession.query(models.Device).filter_by(id=request.form.get('remove_link_token_to_device_device_id')).first()

    if not device:
        error = True
        flash('Device with id %d was not found.' % request.form['link_token_device_id'], 'danger')

    token = sqlsession.query(models.Token).filter_by(id=request.form.get('remove_link_token_to_device_token_id')).first()
    if not token:
        error = True
        flash('Token with id %d was not found.' % request.form['link_token_id'], 'danger')

    if not error:
        device.tokens.remove(token)
        flash('Token with id %d has no longer access on device %s' % (token.id, device.name), 'success')

    return redirect(url_for('tokens', id=token.id))


@app.route('/token_flashed', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def token_flashed(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form.get('token_id')).first()

    if not token:
        return 'False'

    if token.flashed:
        return 'True'
    return 'False'


@app.route('/flash_token', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def flash_token(sqlsession):
    token = sqlsession.query(models.Token).filter_by(id=request.form.get('token_id')).first()
    device = sqlsession.query(models.Device).filter_by(id=config.config('flash_device')).first()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.api_host, config.api_port))
    temporary_token = temporary_token = helpers.generate_token()
    q = Query()
    q.create_register_webui(config.webui_token, temporary_token)
    s.send(q.to_command())
    q.create_flash(temporary_token, token.value, device.pubkey)
    s.send(q.to_command())
    q.create_unregister(temporary_token)
    s.send(q.to_command())
    s.close()

    return redirect(url_for('tokens', id=token.id))