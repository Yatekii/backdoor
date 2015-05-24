import helpers
from query import Query
import config
from models import Device, Token, ServiceData
from models import Type


__service_name__ = 'lock'
__description__ = 'A doormanager which can play a welcome sound.'
__fields__ = (('path', 'path to a sound file', Type.text, '.', ()), )
__uses_blueprint__ = True


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
    backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')


@helpers.handle_dbsession()
def query_sound_request(sqlsession, backdoor, query):
    response = Query(service=__service_name__)
    if len(query.params) == 1:
        token = sqlsession.query(Token).filter_by(value=query.params[0]).first()
        device = sqlsession.query(Device).filter_by(pubkey=query.token).first()
        if token in device.tokens and token.expiry_date >= helpers.today():
            sound_id = sqlsession.query(ServiceData).filter_by(user=token.owner, device=device, key='path').first().value
            response.create_sound_request(config.server_token, query.params[0], sound_id)
            backdoor.logger.info('Granted sound id for token %s to device %s' % (query.params[0], query.token))
        else:
            response.create_sound_request(config.server_token, query.params[0], None)
            backdoor.logger.info('Denied sound id for token %s to device %s' % (query.params[0], query.token))

        backdoor.issue_query(query.token, response)
    else:
        backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')



__methods__ = {
    'OPEN':     (query_open, 'request to open a door')
}