#!/usr/bin/env python

import uuid
import json
import unittest
import gymie.server as server
import gymie.api as api
import numpy as np
from functools import reduce
from test_base import TestBase
from gymie.exceptions import *


class TestGymie(TestBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def assert_valid_state(self, state, size=4):
        self.assertTrue(len(state) == size)
        self.assertTrue(reduce(lambda a, b: type(b) == float and a, state, True)) # all floats

    def test_message_handle(self):
        server.message_handle(self.ws, 'Wrong JSON')
        self.ws.close.assert_called_with((1003, 'Message `Wrong JSON` is invalid'))

        server.message_handle(self.ws, '{"prop": "value"}')
        self.ws.close.assert_called_with((1003, "Message keys ['prop'] are missing or invalid"))

        server.message_handle(self.ws, '{"method": "make"}')
        self.ws.close.assert_called_with((1003, "Message keys ['method'] are missing or invalid"))

        server.message_handle(self.ws, '{"method": "invalid_method", "params": {}}')
        self.ws.close.assert_called_with((1007, 'Method `invalid_method` not found'))

        server.message_handle(self.ws, '{"method": "make", "params": {}}')
        self.ws.close.assert_called_with((1007, 'Parameters `{}` are wrong'))

        server.message_handle(self.ws, '{"method": "make", "params": {"env_id": "malformed" }}')
        self.ws.close.assert_called_with((1007, 'Environment `malformed` is malformed'))

        server.message_handle(self.ws, '{"method": "make", "params": {"env_id": "NotFound-v1" }}')
        self.ws.close.assert_called_with((1007, 'Environment `NotFound-v1` not found'))

        # TODO: test more exceptions
    
    def test_get_env(self):
        with self.assertRaises(EnvironmentMalformed):
            env = api.get_env('malformed')
        with self.assertRaises(EnvironmentNotFound):
            env = api.get_env('NotFound-v1')
        
        env = api.get_env('CartPole-v1')
        self.assertTrue(env.spec.id == 'CartPole-v1')

    def test_make(self):
        with self.assertRaises(EnvironmentMalformed):
            api.make(self.ws, 'malformed')
        
        with self.assertRaises(EnvironmentNotFound):
            api.make(self.ws, 'NotFound-v1')

        api.make(self.ws, 'CartPole-v1')

        instance_id = self.ws.send.call_args[0][0]

        self.assertTrue(type(instance_id) == str)
        self.assertTrue(len(instance_id) == len(uuid.uuid4().hex))
    
    def test_lookup_env(self):
        instance_id = self.make_env('CartPole-v1')

        env = api.lookup_env(instance_id)

        self.assertTrue(env.spec.id == 'CartPole-v1')

        with self.assertRaises(InstanceNotFound):
            api.lookup_env('not_found')

    def test_reset(self):
        instance_id = self.make_env('CartPole-v1')
        api.reset(self.ws, instance_id)

        state = json.loads(self.ws.send.call_args[0][0])
        self.assert_valid_state(state)

    def test_close(self):
        instance_id = self.make_env('CartPole-v1')
        env = api.lookup_env(instance_id)
        self.assertTrue(env != None)

        api.close(self.ws, instance_id)
        with self.assertRaises(InstanceNotFound):
            api.lookup_env(instance_id)
        
        resp = json.loads(self.ws.send.call_args[0][0])
        self.assertTrue(resp)

    def test_step(self):
        instance_id = self.make_env('CartPole-v1')
        env = api.lookup_env(instance_id)

        api.reset(self.ws, instance_id)

        with self.assertRaises(WrongAction):
            api.step(self.ws, instance_id, 'invalid_action')
        
        # valid action
        action = env.action_space.sample()
        api.step(self.ws, instance_id, action)

        observation, reward, done, info = json.loads(self.ws.send.call_args[0][0])

        self.assert_valid_state(observation)
        self.assertTrue(type(reward) == float)
        self.assertTrue(type(done) == bool)
        self.assertTrue(type(info) == dict)

    def test_observation_space(self):
        instance_id = self.make_env('CartPole-v1')
        env = api.lookup_env(instance_id)

        api.observation_space(self.ws, instance_id)
        info = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(info['name'], 'Box')
        self.assertEqual(info['shape'], list(env.observation_space.shape))
        self.assertEqual(info['low'], list(env.observation_space.low))
        self.assertEqual(info['high'], list(env.observation_space.high))

    def test_action_space(self):
        instance_id = self.make_env('CartPole-v1')
        env = api.lookup_env(instance_id)

        api.action_space(self.ws, instance_id)
        info = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(info['name'], 'Discrete')
        self.assertEqual(info['n'], env.action_space.n)

    def test_action_sample(self):
        instance_id = self.make_env('CartPole-v1')
        env = api.lookup_env(instance_id)

        api.action_sample(self.ws, instance_id)
        action = json.loads(self.ws.send.call_args[0][0])

        self.assertTrue(action in range(env.action_space.n))
    
    def test_continuous_action(self):
        instance_id = self.make_env('MountainCarContinuous-v0')
        env = api.lookup_env(instance_id)

        api.action_sample(self.ws, instance_id)
        action = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(np.array(action).shape, env.action_space.shape)


if __name__ == '__main__':
    unittest.main()
