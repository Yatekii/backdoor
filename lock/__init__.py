from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

import helpers
from query import Query
import config
from models import Device, Token, User
from models import Base

__service_name__ = 'lock'
__description__ = 'A doormanager which can play a welcome sound.'
__uses_blueprint__ = True


class Track(Base):
    __tablename__ = __service_name__ + '_tracks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    path = Column(String)


class ActiveTrack(Base):
    __tablename__ = __service_name__ + '_active_tracks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    device_id = Column(Integer, ForeignKey(Device.__tablename__ + '.id'))
    device = relationship('Device', lazy=False, backref='active_tracks')
    track_id = Column(Integer, ForeignKey(Track.__tablename__ + '.id'))
    track = relationship('Track', lazy=False, backref='active_tracks')
    user_id = Column(Integer, ForeignKey(User.__tablename__ + '.id'))
    user = relationship('User', lazy=False, backref='aktive_tracks')


__models__ = [Track, ActiveTrack]

@helpers.handle_dbsession()
def query_open(sqlsession, backdoor, query):
    response = Query(service=__service_name__)
    if len(query.params) == 1:
        if query.token in backdoor.connection_manager.webuis:
            response.create_open(config.server_token)
            backdoor.issue_query(query.params[0], response)
            device_to_open = sqlsession.query(Device).filter_by(pubkey=query.params[0]).first()
            backdoor.logger.debug('Sent OPEN to device %s.' % device_to_open.name)
        else:
            backdoor.logger.info('Requested flash came from a non webui or an unregistered one. It was discarded.')
    else:
        backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')


@helpers.handle_dbsession()
def query_sound_request(sqlsession, backdoor, query):
    response = Query(service=__service_name__)
    if query.query['cmd']['ask']:
        token = sqlsession.query(Token).filter_by(value=query.query['cmd']['token']).first()
        device = sqlsession.query(Device).filter_by(pubkey=query.token).first()
        if token in device.tokens and token.expiry_date >= helpers.today():
            path = sqlsession.query(User).filter_by(user=token.owner, device=device).first().path
            response.create_sound_request(config.server_token, query.query['cmd']['token'], False, path)
            backdoor.logger.info('Granted sound id for token %s to device %s' % (query.query['cmd']['token'], query.token))
        else:
            response.create_sound_request(config.server_token, query.query['cmd']['token'], False, None)
            backdoor.logger.info('Denied sound id for token %s to device %s' % (query.query['cmd']['token'], query.token))

        backdoor.issue_query(query.token, response)
    else:
        backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')



__methods__ = {
    'OPEN':     (query_open, 'request to open a door'),
    'SOUND REQUEST':     (query_sound_request, 'request sound id for a token on a door')
}
