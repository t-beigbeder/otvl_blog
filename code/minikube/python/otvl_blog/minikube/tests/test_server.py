import logging
import sys
import os
import json

import pytest
import yaml

import otvl_blog.minikube.server


logger = logging.getLogger(__name__)


def body_to_obj(json_bytes):
    return json.loads(json_bytes.decode("utf-8"))


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    sys.argv = ["main"]
    monkeypatch.setenv('LOGGING', 'INFO')
    monkeypatch.setenv('CONFIG_DIR', 'code/minikube/data/tests')
    monkeypatch.setenv('CONFIG_NAME', 'test_unit_server')


@pytest.fixture
def app():
    config_dir = os.getenv('CONFIG_DIR', 'code/config')
    config_name = os.getenv('CONFIG_NAME', "undefined_config_name") + '.yml'
    with open(f"{config_dir}/{config_name}") as ysd:
        config = yaml.load(ysd, Loader=yaml.FullLoader)
    return otvl_blog.minikube.server.make_otvl_app(config)


@pytest.mark.gen_test
def test_version(http_client, base_url):
    response = yield http_client.fetch(base_url + "/api/version")
    assert response.code == 200
    resp_o = body_to_obj(response.body)
    assert resp_o == "1.0"


if __name__ == "__main__":
    # pytest.main()
    pytest.main(['-v', '-s', '-k', 'test_server.py'])
