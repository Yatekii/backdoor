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


from flask import redirect, url_for
from flask import Blueprint


import helpers


from webui.wrappers import check_session


blueprint = Blueprint('miscellaneous', __name__, template_folder='templates')

@blueprint.route('/sounds/', defaults={'attribute': 'default', 'value': 'all'})
@blueprint.route('/sounds/<attribute>/<value>/', methods=['POST', 'GET'])
@check_session()
@helpers.handle_dbsession()
def sounds(sqlsession, attribute, value):
    active = 'sounds'
    return redirect(url_for('device.view'))


@blueprint.route('/logs')
@check_session()
def logs():
    active = 'logs'
    return redirect(url_for('user.view'))