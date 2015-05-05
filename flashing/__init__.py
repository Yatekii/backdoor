import helpers
from query import Query
import config
from models import Token


__service_name__ = 'flashing'
__description__ = 'Basic token flashing service'
__fields__ = ()
__uses_blueprint__ = True


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


__methods__ = {
    'FLASH':    (query_flash, 'sent from a webui to request the flashing of a token on a certain device\
                                \nsent from the server to request the flashing of a token on a certain device'),
    'FLASHED':  (query_flashed, 'issued from a device if it successfully flashed a token')
}