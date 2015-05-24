import helpers
from query import Query
import config
from models import Token, Device, User


__service_name__ = 'basics'
__description__ = 'Provides basic commands to authenticate and establish/quit connections'
__fields__ = ()
__uses_blueprint__ = False


@helpers.handle_dbsession()
def query_access(sqlsession, backdoor, query):
    response = Query(service=__service_name__)
    if len(query.params) == 1:
        token = sqlsession.query(Token).filter_by(value=query.params[0]).first()
        device = sqlsession.query(Device).filter_by(pubkey=query.token).first()
        if token in device.tokens and token.expiry_date >= helpers.today():
            response.create_grant(config.server_token, query.params[0])
            backdoor.logger.info('Granted access to token %s at device %s' % (query.params[0], query.token))
        else:
            response.create_deny(config.server_token, query.params[0])
            backdoor.logger.info('Denied access to token %s at device %s' % (query.params[0], query.token))

        backdoor.issue_query(query.token, response)
    else:
        backdoor.logger.debug('Broken query. Expected exactly 1 parameter.')


@helpers.handle_dbsession()
def query_info(sqlsession, backdoor, query):
    response = Query(service=__service_name__)
    if len(query.params) == 1:
        token = sqlsession.query(Token).filter_by(value=query.params[0]).first()
        device = sqlsession.query(Device).filter_by(pubkey=query.token).first()
        if token in device.tokens and token.expiry_date >= helpers.today():
            response.create_info(config.server_token, query.params[0], token.user)
            backdoor.logger.info('Granted info for token %s to device %s' % (query.params[0], query.token))
        else:
            response.create_info(config.server_token, query.params[0], None)
            backdoor.logger.info('Denied info for token %s to device %s' % (query.params[0], query.token))

        backdoor.issue_query(query.token, response)
    else:
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