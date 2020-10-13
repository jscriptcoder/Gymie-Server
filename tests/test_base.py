import unittest
from unittest import TestCase
from unittest.mock import MagicMock
from gymie.api import envs, make


class WebsocketMock():
    def send(self, message):
        pass

    def close(self, close_data=None):
        pass


class TestBase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ws = WebsocketMock()
        ws.send = MagicMock()
        ws.close = MagicMock()
        self.ws = ws

    def tearDown(self):
        keys = list(envs.keys())
        for instance_id in keys:
            del envs[instance_id]
    
    def make_env(self, env_id):
        make(self.ws, env_id)
        return self.ws.send.call_args[0][0]
