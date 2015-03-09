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


import hashlib

from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import session
from flask import Blueprint


import helpers
import models


blueprint = Blueprint('authentication', __name__, template_folder='templates')


@blueprint.route('/login', methods=['GET', 'POST'])
@helpers.handle_dbsession()
def login(sqlsession):
    if request.method == 'POST':
        password = hashlib.sha256(request.form['password'].encode('utf-8'))
        user = sqlsession.query(models.User).filter_by(username=request.form['username'].lower(), password=password.hexdigest()).first()
        if 'failed_attempts' not in session:
            session['failed_attempts'] = 0
        if user and user.level > 9000:
            session['username'] = user.username
            session.permanent = True
            session.pop('failed_attempts', None)
            return redirect(url_for('profile.general'))
        flash('Wrong password, username or permission.', 'danger')
        session['failed_attempts'] = int(session['failed_attempts']) + 1
        return render_template('login.html', username=request.form['username'])
    if 'username' in session:
        return redirect(url_for('profile.general'))
    return render_template('login.html')


@blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('authentication.login'))