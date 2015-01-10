import json

from flask import Flask
from flask import request
from flask import render_template

import config
import backdoor


app = Flask(__name__)

def contains_secret():
	return 'shared_secret' in request.args and request.args['shared_secret'] == config.shared_secret

def is_get():
	return request.method == 'GET'

@app.route('/', methods = ['POST', 'GET'])
def home():
	if is_get() and contains_secret():
		return json.dumps(backdoor.list_user())
		return render_template('list_user.html', data = backdoor.list_user())
	else:
		return render_template('access_denied.html')
