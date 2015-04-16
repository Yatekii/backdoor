import helpers
from query import Query
import config
from models import Token, Device


__service_name__ = 'basics'
__description__ = 'Provides basic commands to authenticate and establish/quit connections'
__fields__ = ()


@helpers.handle_dbsession()
def query_access(sqlsession, backdoor, query):
    response = Query(service=__service_name__)
    token = sqlsession.query(Token).filter_by(value=query.params[0]).first()
    device = sqlsession.query(Device).filter_by(pubkey=query.token).first()
    if len(query.params) == 1:
        if token in device.tokens and token.expiry_date >= helpers.today():
            response.create_grant(config.server_token, query.params[0])
            backdoor.logger.info('Granted access to token %s at device %s' % (query.params[0], query.token))
        else:
            response.create_deny(config.server_token, query.params[0])
            backdoor.logger.info('Denied access to token %s at device %s' % (query.params[0], query.token))

        backdoor.issue_query(query.token, response)
    else:
        backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')


def query_flash(backdoor, query):
    response = Query(service=__service_name__)
    backdoor.logger.info('Requested flash of token %s at device %s' % (query.params[0], query.params[1]))
    if len(query.params) == 2:
        if query.token in backdoor.connection_manager.webuis:
            response.create_flash(config.server_token, query.params[0])
            backdoor.issue_query(query.params[1], response)
        else:
            backdoor.logger.info('Requested flash came from a non webui or an unregistered one. It was discarded.')
    else:
        backdoor.logger.debug('Broken query. Expected exactly 2 parameters.')


@helpers.handle_dbsession()
def query_flashed(sqlsession, backdoor, query):
    if len(query.params) == 1:
        sqlsession.query(Token).filter_by(value=query.params[0]).first().flashed = True
        backdoor.logger.debug('Token %s was flashed' % query.params[0])
    backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')


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
def query_kick(sqlsession, backdoor, query):
    if len(query.params) == 1:
        if query.token in backdoor.connection_manager.webuis:
            device_to_kick = sqlsession.query(Device).filter_by(pubkey=query.params[0]).first()
            if device_to_kick and device_to_kick.is_online:
                backdoor.connection_manager.devices[device_to_kick.pubkey].shutdown()
            backdoor.logger.debug('Kicked device %s.' % device_to_kick.name)
        else:
            backdoor.logger.info('Requested kick came from a non webui or an unregistered one. It was discarded.')
    else:
        backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')


__methods__ = {
    'ACCESS':   (query_access, 'sent from a device to request access'),
    'KICK':     (query_kick, 'force disconnect a specified device')
}