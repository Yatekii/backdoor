import getopt, sys
import hashlib
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import models


def setup():
	opts, args = getopt.getopt(sys.argv[1:], '', ['create-db', 'create-admin=', 'sound-file='])
	engine = create_engine(config.db, echo = config.sql_debug)
	do_create_db = False
	do_create_admin = False
	admin_name = ''
	admin_sound_file = ''
	print(opts)
	for option, arg in opts:
		if option in ('--create-db'):
			do_create_db = True
		if option in ('--create-admin'):
			do_create_admin = True
		if option in ('--sound-file'):
			admin_sound_file = arg	
	if do_create_db:
		print('Creating DB ...')
		create_db(engine)
		print('Done.')
	if do_create_admin:
		auth_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.token_length))
		secret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.secret_length))
		print('Creating admin using name=%s auth_token=%s and secret=%s with sound_file=%s ...' % (admin_name, admin_sound_file, auth_token, secret))
		print(auth_token)
		create_admin(engine, admin_name, 0, hashlib.sha512(auth_token.encode('utf-8')).hexdigest(), secret, admin_sound_file)
		print('Done.')

def create_db(engine):
	models.Base.metadata.create_all(engine)

def create_admin(engine, name, level, auth_token, secret, welcome_sound):
	admin = models.User(name=name, level=level, auth_token=auth_token, secret=secret, welcome_sound=welcome_sound)
	session_factory = sessionmaker(bind=engine)
	session = session_factory()
	session.add(admin)
	session.commit()
	session.close()

if __name__ == '__main__':
	setup()
