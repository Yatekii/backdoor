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


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib

import config
import models

engine = create_engine(config.db, echo=config.sql_debug)
models.base.Base.metadata.drop_all(engine)
models.base.Base.metadata.create_all(engine)

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