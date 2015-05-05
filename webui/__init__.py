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


import datetime
import importlib
import traceback


from flask import Flask
from flask import abort
from flask import redirect, url_for
from flask import make_response


from webui.blueprints import authentication as authentication
from webui.blueprints import search
from webui.blueprints import control
from webui.blueprints import user
from webui.blueprints import token
from webui.blueprints import device
from webui.blueprints import settings
from webui.blueprints import service
from webui.blueprints import profile


from webui.wrappers import check_secret
import config
import helpers
import models
import services


blueprints = []


app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = config.webui_sessions_secret
app.permanent_session_lifetime = datetime.timedelta(days=2048)
app.register_blueprint(authentication.blueprint, url_prefix='/authentication')
app.register_blueprint(search.blueprint, url_prefix='/search')
app.register_blueprint(control.blueprint, url_prefix='/control')
app.register_blueprint(user.blueprint, url_prefix='/user')
app.register_blueprint(token.blueprint, url_prefix='/token')
app.register_blueprint(device.blueprint, url_prefix='/device')
app.register_blueprint(settings.blueprint, url_prefix='/settings')
app.register_blueprint(service.blueprint, url_prefix='/service')
app.register_blueprint(profile.blueprint, url_prefix='/profile')

@helpers.handle_dbsession()
def load_blueprints(sqlsession, app):
    s = sqlsession.query(models.Service).filter_by().all()
    i = 0
    for service in s:
        print('Loading blueprint for service %s' % service.name)
        if load_blueprint(service.name, app):
            blueprints.append(service.name)
            i += 1
            print('Finished loading blueprint for service %s' % service.name)

    print('Loaded %d blueprints' % i if i != 1 else 'Loaded 1 blueprint.')

def load_blueprint(service, app):
    print(blueprints)
    if service not in blueprints:
        try:
            p = importlib.import_module('.%s' % service, 'services')
            m = importlib.import_module('.blueprint', 'services.%s' % service)
            app.register_blueprint(m.__blueprint__, url_prefix='/service_%s' % service)
        except Exception as e:
            print('Failed to load service blueprint %s due to a faulty blueprint' % service)
            print(e)
            return False
    else:
        print('Tried to load a yet loaded blueprint for service %s. Skipping' % service)
        return False
    return True

# print(app.url_map)

@app.route('/')
@check_secret()
def home():
    return redirect(url_for('user.view'))


@app.route('/to_json/<model>', methods=['GET'])
@check_secret()
def to_json(model):
    if model == 'users':
        return helpers.users_to_json_by_filter()
    elif model == 'devices':
        return helpers.devices_to_json_by_filter()
    abort(403)


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Set Cookie')
    response.set_cookie('bastli_backdoor_shared_secret', 'VERYSECUREPASSPHRASE')
    return response