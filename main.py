import backdoor_webui
import config

if __name__ == '__main__':
    app = backdoor_webui.app.run(host=config.webui_host, port=config.webui_port, debug=config.server_debug, threaded=True)