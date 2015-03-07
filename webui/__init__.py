import datetime


from flask import Flask
from flask import abort
from flask import redirect, url_for
from flask import make_response


from webui.blueprints import search
from webui.blueprints import user
from webui.blueprints import token
from webui.blueprints import device
from webui.blueprints import settings
from webui.blueprints import profile

from webui.wrappers import check_secret
import config
import helpers


app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = config.webui_sessions_secret
app.permanent_session_lifetime = datetime.timedelta(days=2048)
app.register_blueprint(search.blueprint, url_prefix='/search')
app.register_blueprint(user.blueprint, url_prefix='/user')
app.register_blueprint(token.blueprint, url_prefix='/token')
app.register_blueprint(device.blueprint, url_prefix='/device')
app.register_blueprint(settings.blueprint, url_prefix='/settings')
app.register_blueprint(profile.blueprint, url_prefix='/profile')

print(app.url_map)

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