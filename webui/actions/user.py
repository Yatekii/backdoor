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


@app.route('/add_user', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def add_user(sqlsession):
    error = False

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['add_user_email']):
        error = True
        flash('Please enter a valid email address', 'danger')

    try:
        level = int(request.form['add_user_level'])
    except Exception:
        level = -1

    if request.form['add_user_level'] == 'over 9000' or request.form['add_user_level'] == '> 9000' \
            or request.form['add_user_level'] == 'over ninethousand':
        level = 9999

    if level not in range(0, 10000):
        error = True
        flash('Please enter a valid number between 0 and 9999 as the userlevel.', 'danger')

    if sqlsession.query(models.User).filter_by(username=request.form['add_user_username'].lower()).first():
        error = True
        flash('That username exists yet. Please choose a different one.', 'danger')

    if not error:
        password = hashlib.sha256(request.form['add_user_password'].encode('utf-8'))
        user = models.User(
            creation_date=helpers.today(),
            username=request.form['add_user_username'].lower(),
            password=password.hexdigest(),
            name=request.form['add_user_name'],
            level=level,
            email=request.form['add_user_email'],
            nethzid=request.form['add_user_nethzid']
        )
        sqlsession.add(user)
        sqlsession.commit()
        flash('New user was created successfully', 'success')
        return redirect(url_for('users', id=user.id))

    else:
        return redirect(url_for(
            'users',
            user_username=request.form['add_user_username'],
            user_password=request.form['add_user_password'],
            user_name=request.form['add_user_name'],
            user_level=request.form['add_user_level'],
            user_email=request.form['add_user_email'],
            user_nethzid=request.form['add_user_nethzid']
        ))


@app.route('/remove_user', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def remove_user(sqlsession):
    user = sqlsession.query(models.User).filter_by(id=request.form['user_id']).first()

    if user:
        sqlsession.delete(user)
        flash('User %s was removed successfully.' % user.name, 'success')

    else:
        flash('User with id %d was not found.' % request.form['user_id'], 'danger')

    return redirect(url_for('users'))


@helpers.handle_dbsession()
def change_user(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    try:
        level = int(request.form['change_user_level'])
    except Exception:
        level = -1

    if request.form['change_user_level'] == 'over 9000' or request.form['change_user_level'] == '> 9000' or request.form['change_user_level'] == 'over ninethousand':
        level = 999

    if level not in range(0, 10000):
        error = True
        flash('Please enter a valid number between 0 and 9999 as the userlevel.', 'danger')

    if not re.match(r'[\w.-]+@[\w.-]+.\w+', request.form['change_user_email']):
        error = True
        flash('Please enter a valid email address.', 'danger')

    if not error:
        user.level = level
        user.name = request.form['change_user_name']
        user.email = request.form['change_user_email']
        user.nethzid = request.form['change_user_nethzid']
        flash('User %s has been changed.' % (user.name), 'success')

    return redirect(request.referrer)


@helpers.handle_dbsession()
def change_password(sqlsession):
    error = False
    user = sqlsession.query(models.User).filter_by(id=request.form.get('change_user_id')).first()

    if not user:
        error = True
        flash('User with id %s was not found.' % request.form.get('change_user_id'), 'danger')

    if request.form['change_user_password'] != request.form['change_user_password_validation']:
        error = True
        flash('The entered passwords do not match.', 'danger')

    if not error:
        password = hashlib.sha256(request.form['change_user_password'].encode('utf-8'))
        user.password = password.hexdigest()
        flash('The password has ben changed.', 'success')

    return redirect(url_for('profile', category='password'))