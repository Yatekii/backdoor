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


from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import Blueprint


import helpers
import models
from webui.wrappers import check_session, check_rights
from webui.permission_flags import *

__blueprint__ = Blueprint('service_flashing', __name__, template_folder='templates')


@__blueprint__.route('/view', defaults={'id': '0'})
@__blueprint__.route('/view/<id>', methods=['POST', 'GET'])
@check_session()
@check_rights(0)
@helpers.handle_dbsession()
def view(sqlsession, id):
    active = 'service'
    id = int(id)

    services = sqlsession.query(models.Service).filter_by(uses_blueprint=True).order_by(models.Service.name.asc()).all()
    service = sqlsession.query(models.Service).filter_by(id=id).first()
    return render_template(
        'main.html',
        active=active,
        id=id,
        service=service,
        services=services
    )