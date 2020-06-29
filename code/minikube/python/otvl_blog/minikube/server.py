import logging
import os
import argparse
import json
import yaml
import traceback
import sys

import tornado.ioloop
import tornado.web


logger = logging.getLogger(__name__)


def setup_env():
    logging.basicConfig(
        level=os.getenv('LOGGING', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class BaseHandler(tornado.web.RequestHandler):
    logger = logging.getLogger(__module__ + '.' + __qualname__)  # noqa
    server_config = {}

    def _request_summary(self):
        if 'User-Agent' in self.request.headers:
            ua = self.request.headers['User-Agent']
        else:
            ua = "undefined_User-Agent"
        if 'X-Forwarded-For' in self.request.headers:
            xff = self.request.headers['X-Forwarded-For']
        else:
            xff = "undefined_X-Forwarded-For"

        s = "%s %s (%s) (%s)" % (
            self.request.method,
            self.request.uri,
            xff,
            ua
        )
        return s

    def initialize(self, **kwargs):
        BaseHandler.server_config = kwargs["server_config"]
        del kwargs["server_config"]
        super().initialize(**kwargs)

    def prepare(self):
        if 'User-Agent' in self.request.headers:
            ua = self.request.headers['User-Agent']
        else:
            ua = "undefined_User-Agent"
        self.logger.debug(f"prepare: {ua} {self.request.method} {self.request.path}")
        if self.request.path.startswith("/api"):
            self.set_header("Content-Type", "application/json")
        else:
            self.set_header("Content-Type", "text/html")

    def _check_par(self, name, par):
        if not par:
            self._error(400, 'MissingParameter', 'Parameter {0} is missing in URL'.format(name))
            return par
        return True

    def _error(self, code, reason, message):
        self.set_status(code)
        self.finish({'reason': reason, 'message': message})


class VersionHandler(BaseHandler):
    logger = logging.getLogger(__module__ + '.' + __qualname__)  # noqa

    def initialize(self, **kwargs):
        super().initialize(**kwargs)

    def get(self):
        self.write(json.dumps(self.server_config["version"], indent=2))
        return self.finish()


class AppServerMainBase:
    logger = logging.getLogger(__module__ + '.' + __qualname__)  # noqa
    server_config = None

    def _arg_parser(self):
        raise NotImplementedError("_arg_parser")

    def __init__(self, name):
        self.name = name
        self.arg_parser = self._arg_parser()
        self.args = None
        self.config_file = None

    def _do_run(self):
        raise NotImplementedError("_do_run")

    def pre_load_config(self):
        pass

    def _do_load_config(self):
        raise NotImplementedError("_do_load_config")

    def _load_config(self):
        self.logger.debug("load_config")
        self.pre_load_config()
        if self.config_file is None:
            config_dir = os.getenv('CONFIG_DIR', '/config')
            config_name = os.getenv('CONFIG_NAME', self.name) + '.yml'
            self.config_file = f"{config_dir}/{config_name}"
        with open(self.config_file) as ysd:
            self.__class__.server_config = yaml.load(ysd, Loader=yaml.FullLoader)
        self._do_load_config()

    def run(self):
        self.args = self.arg_parser.parse_args()
        try:
            self._load_config()
            self.logger.info('run: start')
            result = self._do_run()
            self.logger.info('run: done')
            return result
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                'An unkonwn error occured, please contact the support - {0} {1}'.format(
                    type(e), e))
        self.logger.info('run: done')
        return False


def make_otvl_app(server_config):
    handler_kwa = {
        "server_config": server_config
        }
    return tornado.web.Application([
        (r"/api/version/?", VersionHandler, handler_kwa)
    ])


class OtvlServer(AppServerMainBase):
    logger = logging.getLogger(__module__ + "." + __qualname__)  # noqa

    @classmethod
    def _make_app(cls):
        return make_otvl_app(cls.server_config)

    def _arg_parser(self):
        parser = argparse.ArgumentParser(description='OtvlServer')
        parser.add_argument('-c', '--config', type=str, help='Configuration file')
        parser.add_argument('-p', '--port', type=int, help='port to bind the server (defaults to OW_PORT env var or 8888)')  # noqa
        parser.add_argument('-a', '--address', type=str, help='host or IP address to listen to, empty string implies all interfaces (defaults to OW_ADDRESS or empty)')  # noqa
        return parser

    def __init__(self, name):
        AppServerMainBase.__init__(self, name)

    def pre_load_config(self):
        self.logger.debug("pre_load_config OtvlServer")
        self.config_file = self.args.config

    def _do_load_config(self):
        self.logger.debug("_do_load_config OtvlServer")

    def _do_run(self):
        self.logger.debug("_do_run OtvlServer")
        if self.args.port:
            port = self.args.port
        else:
            port = int(os.getenv("OW_PORT", "8989"))
        if self.args.address:
            address = self.args.address
        else:
            address = os.getenv("OW_ADDRESS", "")
        app = self._make_app()
        app.listen(port, address)
        tornado.ioloop.IOLoop.current().start()
        return True


setup_env()

if __name__ == "__main__":
    cmd_name = os.path.basename(sys.argv[0]).split('.')[0]
    res = OtvlServer(cmd_name).run()
    sys.exit(0 if res else -1)
