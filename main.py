import webui
import config

if __name__ == '__main__':
    app = webui.app.run(host=config.webui_host, port=config.webui_port, debug=config.server_debug, use_evalex=False, threaded=True)