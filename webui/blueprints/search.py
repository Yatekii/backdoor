from flask import render_template
from flask import request
from flask import Blueprint


import helpers
import models


from webui.wrappers import check_session


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

    users = sqlsession.query(models.User).filter(models.User.name.like('%' + request.args.get('q') + '%')).all()
    devices = sqlsession.query(models.Device).filter(models.Device.name.like('%' + request.args.get('q') + '%')).all()
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