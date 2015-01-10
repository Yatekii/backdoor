import mappings
import config

if __name__ == '__main__':
	mappings.app.run(host=config.host, port=config.port, debug=config.server_debug)
