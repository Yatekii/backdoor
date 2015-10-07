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


from flask import render_template
from flask import request
from flask import Blueprint


import helpers
import models


from webui.wrappers import check_session
from sqlalchemy import or_


blueprint = Blueprint('search', __name__, template_folder='templates')


@blueprint.route('/', defaults={'type' : 'list', 'id': '0'})
@blueprint.route('/<type>/<id>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def search(sqlsession, type, id):
    id = int(id)
    active = 'search'

    user = None
    if id > 0:
        user = sqlsession.query(models.User).filter_by(id=int(id)).first()

    device = None
    if id > 0:
        device = sqlsession.query(models.Device).filter_by(id=id).first()

    users = sqlsession.query(models.User).filter(
        or_(
            models.User.name.like('%' + request.args.get('q') + '%'),
            models.User.username.like('%' + request.args.get('q') + '%'))
        ).all()
    devices = sqlsession.query(models.Device).filter(
            models.Device.name.like('%' + request.args.get('q') + '%')
        ).all()
    return render_template(
        'search.html',
        active=active,
        date=helpers.today(),
        id=id,
        q=request.args.get('q'),
        type=type,
        user=user,
        users=users,
        device=device,
        devices=devices
    )