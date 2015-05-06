import socket

from models.base import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
import helpers
import models.device
from query import Query
import config


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    value = Column(String)
    description = Column(String)
    flashed = Column(Boolean)
    expiry_date = Column(Date)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='cascade'))


    @helpers.handle_dbsession()
    def add(sqlsession, **kwargs):
        error = False
        errors = []
        name = None
        description = None
        expiry_date = None
        owner = None

        for attribute in kwargs:
            if attribute == 'owner':
                if type(kwargs[attribute]) == int:
                    owner = sqlsession.query(models.User).filter_by(id=owner).first()

                if not owner:
                    if 'owner_name' in kwargs:
                        owner_query = sqlsession.query(models.User).filter_by(name=kwargs['owner_name'])
                        if owner_query.count() == 1:
                            owner = owner_query.first()
                        else:
                            error = True
                            errors.append(('owner', 'User was not found.'))
                    else:
                        error = True
                        errors.append(('owner', 'User was not found.'))

            elif attribute == 'expiry_date':
                try:
                    expiry_date = helpers.str_to_date(kwargs[attribute])
                except BaseException:
                    error = True
                    errors.append(('expiry_date', 'Expiry date has a bad format. It should be YYYY-mm-dd.'))

            elif attribute == 'name':
                name = kwargs[attribute]

            elif attribute == 'description':
                description = kwargs[attribute]

            else:
                pass

        if not error:
            token = models.Token(
                name=name,
                value=helpers.generate_token(),
                description=description,
                owner=owner,
                flashed=False,
                expiry_date=expiry_date,
                creation_date=helpers.today()
            )
            sqlsession.add(token)
            sqlsession.commit()
            return token.id, None

        else:
            return False, errors


    @helpers.handle_dbsession()
    def activate(sqlsession, token):
        if type(token) == int:
            token = sqlsession.query(models.Token).filter_by(id=token).first()

        if token:
            for date in config('semester_end_dates'):
                date = helpers.str_to_date(date)
                if date <= helpers.today():
                    continue
                token.expiry_date = date
                return date
        return False


    @helpers.handle_dbsession()
    def flash(sqlsession, token, device):
        error = False
        errors = []
        token = sqlsession.query(models.Token).filter_by(id=token).first()
        device = sqlsession.query(models.Device).filter_by(id=device).first()

        if device:
            if token:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((config.api_host, config.api_port))
                    temporary_token = helpers.generate_token()
                    q = Query()
                    q.create_register_webui(config.webui_token, temporary_token)
                    s.send(q.to_command())
                    q.create_flash(temporary_token, token.value, device.pubkey)
                    s.send(q.to_command())
                    q.create_unregister(temporary_token)
                    s.send(q.to_command())
                    s.close()
                except Exception:
                    error = True
                    errors.append(('flash', 'Connection to device failed.'))
            else:
                error = True
                errors.append(('token', 'Token does not exist.'))
        else:
                error = True
                errors.append(('device', 'Device does not exist.'))
        return error, errors
