#!/usr/bin/env python

import uuid
import json
import retro
import unittest
import numpy as np
import gymie.server as server
import gymie.api as api
from functools import reduce
from test_base import TestBase
from gymie.exceptions import *


def retro_get_env(env_id, seed=None):
    try:
        env = retro.make(game=env_id)
    except FileNotFoundError:
        raise EnvironmentNotFound
    else:
        if seed: 
            env.seed(seed)
        
        return env


class TestGymieRetro(TestBase):

    @classmethod
    def setUpClass(cls):
        api.defs['get_env'] = retro_get_env

    @classmethod
    def tearDownClass(cls):
        api.defs['get_env'] = api.get_env
    
    def assert_valid_state(self, state, shape=(224, 320, 3)):
        self.assertTrue(type(state) == list)
        self.assertEqual(np.array(state).shape, shape)
    
    def test_get_env(self):
        with self.assertRaises(EnvironmentNotFound):
            env = api.defs['get_env']('not_found')
        
        env = api.defs['get_env']('Airstriker-Genesis')
        self.assertTrue(env.gamename == 'Airstriker-Genesis')
    
    def test_make(self):
        with self.assertRaises(EnvironmentNotFound):
            api.make(self.ws, 'not_found')

        api.make(self.ws, 'Airstriker-Genesis')

        instance_id = self.ws.send.call_args[0][0]

        self.assertTrue(type(instance_id) == str)
        self.assertTrue(len(instance_id) == len(uuid.uuid4().hex))
    
    def test_lookup_env(self):
        instance_id = self.make_env('Airstriker-Genesis')

        env = api.lookup_env(instance_id)

        self.assertTrue(env.gamename == 'Airstriker-Genesis')

        with self.assertRaises(InstanceNotFound):
            api.lookup_env('not_found')
    
    def test_reset(self):
        instance_id = self.make_env('Airstriker-Genesis')
        api.reset(self.ws, instance_id)

        state = json.loads(self.ws.send.call_args[0][0])
        self.assert_valid_state(state)
    
    def test_close(self):
        instance_id = self.make_env('Airstriker-Genesis')
        env = api.lookup_env(instance_id)
        self.assertTrue(env != None)

        api.close(self.ws, instance_id)
        with self.assertRaises(InstanceNotFound):
            api.lookup_env(instance_id)
        
        resp = json.loads(self.ws.send.call_args[0][0])
        self.assertTrue(resp)

    def test_step(self):
        instance_id = self.make_env('Airstriker-Genesis')
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
        instance_id = self.make_env('Airstriker-Genesis')
        env = api.lookup_env(instance_id)

        api.observation_space(self.ws, instance_id)
        info = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(info['name'], 'Box')
        self.assertEqual(info['shape'], list(env.observation_space.shape))
        self.assertEqual(info['low'], env.observation_space.low.tolist())
        self.assertEqual(info['high'], env.observation_space.high.tolist())

    def test_action_space(self):
        instance_id = self.make_env('Airstriker-Genesis')
        env = api.lookup_env(instance_id)

        api.action_space(self.ws, instance_id)
        info = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(info['name'], 'MultiBinary')
        self.assertEqual(info['n'], env.action_space.n)
        self.assertEqual(info['shape'], [env.action_space.n])
        self.assertEqual(info['low'], [0])
        self.assertEqual(info['high'], [1])

    def test_action_sample(self):
        instance_id = self.make_env('Airstriker-Genesis')
        env = api.lookup_env(instance_id)

        api.action_sample(self.ws, instance_id)
        action = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(np.array(action).shape, env.action_space.shape)


if __name__ == '__main__':
    unittest.main()
