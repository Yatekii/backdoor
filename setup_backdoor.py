import getopt
import sys
import hashlib
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import models


def setup():
    opts, args = getopt.getopt(sys.argv[1:], '',
                               ['create-db', 'create-user=', 'remove-user=', 'sound-file=', 'userlevel='])
    engine = create_engine(config.db, echo=config.sql_debug)
    do_create_db = False
    do_create_user = False
    do_remove_user = False
    create_user_name = ''
    remove_user_name = ''
    sound_file = ''
    userlevel = ''
    print(opts)
    for option, arg in opts:
        if option in ('--create-db'):
            do_create_db = True
        if option in ('--create-user'):
            do_create_user = True
            create_user_name = arg
        if option in ('--sound-file'):
            sound_file = arg
        if option in ('--remove-user'):
            do_remove_user = True
            remove_user_name = arg
        if option in ('--userlevel'):
            userlevel = arg

    if do_create_db:
        print('Creating DB ...')
        create_db(engine)
        print('Done.')
    if do_create_user:
        auth_token = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.token_length))
        secret = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.secret_length))
        print('Create  user using name=%s auth_token=%s and secret=%s with sound_file=%s ...' % (
        create_user_name, sound_file, auth_token, secret))
        create_user(engine, create_user_name, 0, hashlib.sha512(auth_token.encode('utf-8')).hexdigest(), secret,
                    sound_file)
        print('Done.')

    if do_remove_user:
        auth_token = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.token_length))
        secret = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.secret_length))
        print('Removing admin using name=%s ...' % (remove_user_name))
        remove_user(engine, remove_user_name)
        print('Done.')


def create_db(engine):
    models.Base.metadata.create_all(engine)


def create_user(engine, name, level, auth_token, secret, welcome_sound):
    user = models.User(name=name, level=level, auth_token=auth_token, secret=secret, welcome_sound=welcome_sound)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    session.add(user)
    session.commit()
    session.close()


def remove_user_by_name(engine, name):
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    print(session.query(models.User).all())
    session.delete(session.query(models.User).filter_by(name=name).first())
    session.commit()
    session.close()


if __name__ == '__main__':
    setup(requires=['sqlalchemy'])
