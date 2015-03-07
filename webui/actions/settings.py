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


@app.route('/change_general_settings', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_general_settings(sqlsession):
    error = False

    config.store_config('flash_device', request.form['change_flash_device'])
    config.store_config('default_door_device', request.form['change_default_door_device'])

    dates = []
    for key in request.form:
        if 'change_semester_end_date_' in key:
            try:
                print(request.form[key])
                dates.append(helpers.date_to_str(helpers.str_to_date(request.form[key])))
            except BaseException:
                error = True
                flash('At least one date has a bad format. It should be YYYY-mm-dd!', 'danger')
                break
    if not error:
        sorted_dates = sorted(dates, key=lambda date: helpers.str_to_date(date))
        config.store_config('semester_end_dates', sorted_dates)

    flash('New settings have successfully been stored.', 'success')
    return redirect(url_for('settings'))