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

import functools
from flask import url_for
from flask import redirect
from flask import abort
from flask import request
from flask import session
from flask import flash


import config
import helpers
import models


def check_secret():
    def checker_helper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            request.cookies.get('bastli_backdoor_shared_secret') == config.api_token
            if True:
                return f(*args, **kwargs)
            else:
                abort(403)
        return inner
    return checker_helper


def check_session():
    def checker_helper(f):
        @functools.wraps(f)
        @helpers.handle_dbsession()
        def inner(sqlsession, *args, **kwargs):
            if 'username' in session\
                    and sqlsession.query(models.User).filter_by(username=session['username']).count() == 1:
                return f(*args, **kwargs)
            else:
                flash('Sorry, you are not logged in. Please login first.')
                return redirect(url_for('authentication.login'))
        return inner
    return checker_helper


def check_rights(flag):
    def checker_helper(f):
        @functools.wraps(f)
        @helpers.handle_dbsession()
        def inner(sqlsession, *args, **kwargs):
            level = sqlsession.query(models.User).filter_by(id=session['id']).first().level
            if (level & flag) > 0 or flag == 0:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('authentication.forbidden'))
        return inner
    return checker_helper