import functools
from flask import url_for
from flask import redirect
from flask import abort
from flask import request
from flask import session


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

            if 'username' in session and sqlsession.query(models.User).filter_by(username=session['username']).count() == 1:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('authentication.logout'))

        return inner

    return checker_helper