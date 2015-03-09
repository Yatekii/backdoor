import re
import hashlib

from models.base import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
import helpers
from webui import permission_flags
import models.device


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    username = Column(String)
    password = Column(String)
    level = Column(Integer)
    name = Column(String)
    email = Column(String)
    nethzid = Column(String)
    welcome_sound = Column(String)
    default_device_id = Column(Integer, ForeignKey('devices.id'))
    tokens = relationship('Token', lazy='dynamic', backref='owner', cascade='all, delete-orphan')


    @helpers.handle_dbsession()
    def add(sqlsession, **kwargs):
        error = False
        errors = []
        username = None
        password = None
        level = None
        name = None
        email = None
        nethzid = None

        for attribute in kwargs:

            if attribute == 'username':
                existing_user = sqlsession.query(User).filter_by(username=kwargs[attribute].lower()).first()
                if existing_user:
                    error = True
                    errors.append(('username', 'Username is already taken.'))
                else:
                    username = kwargs[attribute]

            elif attribute == 'password':
                if len(kwargs[attribute]) < 8:
                    error = True
                    errors.append(('password', 'Please enter a password of at least 8 signs.'))
                else:
                    password = hashlib.sha256(kwargs[attribute].encode('utf-8'))

            elif attribute == 'level':
                if kwargs[attribute] == 'over 9000' or kwargs[attribute] == '> 9000' or kwargs[attribute] == 'over ninethousand':
                    kwargs[attribute] = 16384
                if kwargs[attribute] == '':
                    kwargs[attribute] = 0
                try:
                    kwargs[attribute] = int(kwargs[attribute])
                except Exception:
                    pass
                if type(kwargs[attribute]) != int:
                    error = True
                    errors.append(('level', 'Please enter a valid number as the userlevel.'))
                else:
                    level = kwargs[attribute]

            elif attribute == 'name':
                name = kwargs[attribute]

            elif attribute == 'email':
                if not re.match(r'[\w.-]+@[\w.-]+.\w+', kwargs[attribute]):
                    error = True
                    errors.append(('email', 'Please enter a valid email address.'))
                else:
                    email = kwargs[attribute]

            elif attribute == 'nethzid':
                nethzid = kwargs[attribute]

            else:
                pass

        if not error:
            if (((username and password and (level & (permission_flags.OVER_NINETHOUSAND\
            | permission_flags.CAN_LOGIN)) > 0)) or name) and (email or nethzid):
                user = User(
                    creation_date=helpers.today(),
                    username=username,
                    password=password.hexdigest(),
                    name=name,
                    level=level,
                    email=email,
                    nethzid=nethzid
                )
                sqlsession.add(user)
                sqlsession.commit()
                return user.id, None
            else:
                errors.append(('general', 'Failed to create user. You need to at least fill a name and (an email and or a nethzid).'))
        return False, errors


    @helpers.handle_dbsession()
    def change(sqlsession, user, **kwargs):
        error = False
        errors = []
        password = None
        level = None
        name = None
        email = None
        nethzid = None

        if(type(user) == int):
            user = sqlsession.query(User).filter_by(id=user).first()

        if not user:
            error = True
            errors.append(('user', 'User with id %d was not found.' % id))

        for attribute in kwargs:
            if attribute == 'password':
                if len(kwargs[attribute]) < 8:
                    error = True
                    errors.append(('password', 'Please enter a password of at least 8 signs.'))
                    continue
                if kwargs[attribute] != kwargs['password_validate']:
                    error = True
                    errors.append(('password', 'Passwords do not match!'))
                    continue
                password = hashlib.sha256(kwargs[attribute].encode('utf-8'))

            elif attribute == 'level':
                if kwargs[attribute] == 'over 9000' or kwargs[attribute] == '> 9000' or kwargs[attribute] == 'over ninethousand':
                    kwargs[attribute] = 16384
                if type(kwargs[attribute]) == int:
                    error = True
                    errors.append(('level', 'Please enter a valid number as the userlevel.'))
                else:
                    level = kwargs[attribute]

            elif attribute == 'name':
                name = kwargs[attribute]

            elif attribute == 'email':
                if not re.match(r'[\w.-]+@[\w.-]+.\w+', kwargs[attribute]):
                    error = True
                    errors.append(('email', 'Please enter a valid email address.'))
                else:
                    email = kwargs[attribute]

            elif attribute == 'nethzid':
                nethzid = kwargs[attribute]

            elif attribute == 'default_device_id':
                device = sqlsession.query(models.device.Device).filter_by(id=kwargs[attribute]).first()
                if not device:
                    error = True
                    errors.append(('default_device_id', 'Device does not exist.'))
                else:
                    user.default_device_id = kwargs[attribute]

            else:
                pass

        if not error:
            if password: user.password=password.hexdigest()
            if name: user.name=name
            if level: user.level=level
            if email: user.email=email
            if nethzid: user.nethzid=nethzid
            return user.id, None
        else:
            return user.id, errors