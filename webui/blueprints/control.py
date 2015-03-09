"""

    NFC controlled door access.
    Copyright (C) 2015  Yatekii yatekii(at)yatekii.ch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""


import socket

from flask import flash
from flask import redirect
from flask import request
from flask import session
from flask import Blueprint


import config
import helpers
import models
from query import Query
from webui.wrappers import check_session


blueprint = Blueprint('control', __name__, template_folder='templates')


@blueprint.route('/open/', defaults={'id' : '0'})
@blueprint.route('/open/<id>', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def open(sqlsession, id):
    id = int(id)
    user = sqlsession.query(models.User).filter_by(username=session['username']).first()
    device = None
    if id == 0:
        if user.default_device:
            device = user.default_device
        else:
            id = int(config.config('default_door_device'))
    if id > 0 and not device:
        device = sqlsession.query(models.Device).filter_by(id=id).first()

    if device:
        access_granted = False

        if user.level > 9000:
            access_granted = True
        else:
            for token in user.tokens:
                if token in device.tokens:
                    access_granted = True
        if not access_granted:
            flash('No access on device with id %s' % id, 'danger')
        else:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((config.api_host, config.api_port))
                temporary_token = helpers.generate_token()
                q = Query()
                q.create_register_webui(config.webui_token, temporary_token)
                s.send(q.to_command())
                q.create_open(temporary_token, device.pubkey)
                s.send(q.to_command())
                q.create_unregister(temporary_token)
                s.send(q.to_command())
                s.close()
                flash('%s has been opened.' % device.name, 'success')
            except Exception as e:
                flash('Failed to access device %s' % device.name, 'danger')
    else:
        flash('Could not find device with id %s' % id, 'danger')
    return redirect(request.referrer)