from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib

import config
import models

engine = create_engine(config.db, echo=config.sql_debug)
models.Base.metadata.drop_all(engine)
models.Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
s = session_factory()
password = hashlib.sha256(b'1')
u = models.User(
    username='yatekii',
    password=password.hexdigest(),
    level=9999,
    name='Noah Huesser',
    email='noah@bastli.ch',
    nethzid='nhuesser'
)
s.add(u)
s.commit()
s.close()

# gpg = gnupg.GPG(gnupghome='keys')
# gpg.encoding = 'utf-8'
#
# key_data = gpg.gen_key_input(key_type='RSA', key_length=4096, name_real='Backdoor Server', name_email='backdoor@bastli.ch')
# key = gpg.gen_key(key_data)