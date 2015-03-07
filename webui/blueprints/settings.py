from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import Blueprint


import config
import helpers
import models
from webui.wrappers import check_session


blueprint = Blueprint('settings', __name__, template_folder='templates')


@blueprint.route('/readonly', methods=['POST', 'GET'])
@check_session()
def readonly():
    active = 'settings'

    return render_template(
        'settings_readonly.html',
        active=active,
        category='readonly',
        webui_token=config.webui_token,
        server_token=config.server_token,
        api_token=config.api_token
    )


@blueprint.route('/general', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def general(sqlsession):
    active = 'settings'

    devices = sqlsession.query(models.Device).all()
    return render_template(
        'settings_general.html',
        active=active,
        category='general',
        flash_device=config.config('flash_device'),
        default_door_device=config.config('default_door_device'),
        devices=devices,
        semester_end_dates=config.config('semester_end_dates')
    )


@blueprint.route('/change_general', methods=['POST'])
@check_session()
@helpers.handle_dbsession()
def change_general(sqlsession):
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
    return redirect(url_for('settings.general'))