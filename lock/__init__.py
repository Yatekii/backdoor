import helpers
from query import Query
import config
from models import Device
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


__methods__ = {
    'OPEN':     (query_open, 'request to open a door')
}