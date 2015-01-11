import mappings
import config

if __name__ == '__main__':
    print(mappings.app.static_folder)
    mappings.app.run(host=config.host, port=config.port, debug=config.server_debug)
