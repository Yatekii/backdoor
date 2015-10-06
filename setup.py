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
import datetime

engine = create_engine(config.db, echo=config.sql_debug)
models.base.Base.metadata.drop_all(engine)
models.base.Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
s = session_factory()
password = hashlib.sha256(b'1')
u1 = models.User(
    username='yatekii',
    password=password.hexdigest(),
    level=9999,
    name='Noah Huesser',
    email='noah@bastli.ch',
    nethzid='nhuesser'
)
s.add(u1)
password = hashlib.sha256(b'2')
u2 = models.User(
    username='tiwalun',
    password=password.hexdigest(),
    level=9999,
    name='Dominik Boehi',
    email='dominik@bastli.ch',
    nethzid='dboehi'
)
s.add(u2)
d = models.Device(
            name='Der Testgeraet',
            pubkey='alfonso',
            creation_date=datetime.date.today(),
            is_online=False,
            is_enabled=True
        )
s.add(d)
data = '2015-12-01'.split('-')
date = datetime.date(int(data[0]), int(data[1]), int(data[2]))
t = models.Token(
            name='Testtoken Yatekii',
            value='migros',
            description='Bla',
            owner=u1,
            flashed=False,
            expiry_date=date,
            creation_date=datetime.date.today()
            )
d.tokens.append(t)
s.add(t)
t = models.Token(
            name='Testtoken Tiwalun',
            value='random',
            description='Blo',
            owner=u2,
            flashed=False,
            expiry_date=date,
            creation_date=datetime.date.today()
            )
d.tokens.append(t)
s.add(t)
s.commit()
s.close()