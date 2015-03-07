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