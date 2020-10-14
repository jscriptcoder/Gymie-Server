#!/usr/bin/env python

import os
import uuid
import json
import unittest
import numpy as np
import gymie.server as server
import gymie.api as api
from gymie.api import override
from functools import reduce
from test_base import TestBase
from gymie.exceptions import *
from mlagents_envs.environment import UnityEnvironment, UnityEnvironmentException
from gym_unity.envs import UnityToGymWrapper


@override('get_env')
def unity_get_env(file_name, 
                  seed=None, 
                  worker_id=0, 
                  no_graphics=False, 
                  uint8_visual=False, 
                  flatten_branched=False,
                  allow_multiple_obs=False):

    try:
        unity_env = UnityEnvironment(file_name, 
                                        seed=seed, 
                                        worker_id=worker_id, 
                                        no_graphics=no_graphics)
        
        env = UnityToGymWrapper(unity_env, 
                                uint8_visual=uint8_visual, 
                                flatten_branched=flatten_branched, 
                                allow_multiple_obs=allow_multiple_obs)
    except UnityEnvironmentException:
        raise EnvironmentNotFound
    else:
        return env

@override('process_step')
def unity_process_step(step):
    observation, reward, done, info = step
    return observation.tolist(), float(reward), done, {}
    
dir_path = os.path.dirname(os.path.realpath(__file__))
env_path = f'{dir_path}/unity_env/PushBlock.app'

class TestGymieUnity(TestBase):

    def assert_valid_state(self, state, shape=(210,)):
        self.assertTrue(type(state) == list)
        self.assertEqual(np.array(state).shape, shape)
    
    def test_get_env(self):
        with self.assertRaises(EnvironmentNotFound):
            env = api.get_env(f'{dir_path}/not_found')

        env = api.get_env(env_path)
        self.assertTrue(type(env), UnityToGymWrapper)

        env.close()
    
    def test_make(self):
        with self.assertRaises(EnvironmentNotFound):
            api.make(self.ws, 'not_found')

        api.make(self.ws, env_path)

        instance_id = self.ws.send.call_args[0][0]

        self.assertTrue(type(instance_id) == str)
        self.assertTrue(len(instance_id) == len(uuid.uuid4().hex))

        api.close(self.ws, instance_id)

    def test_lookup_env(self):
        instance_id = self.make_env(env_path)

        env = api.lookup_env(instance_id)

        self.assertTrue('PushBlock' in env.name)

        with self.assertRaises(InstanceNotFound):
            api.lookup_env('not_found')
        
        api.close(self.ws, instance_id)

    def test_reset(self):
        instance_id = self.make_env(env_path)
        api.reset(self.ws, instance_id)

        state = json.loads(self.ws.send.call_args[0][0])
        self.assert_valid_state(state)

        api.close(self.ws, instance_id)

    def test_close(self):
        instance_id = self.make_env(env_path)
        env = api.lookup_env(instance_id)
        self.assertTrue(env != None)

        api.close(self.ws, instance_id)
        with self.assertRaises(InstanceNotFound):
            api.lookup_env(instance_id)
        
        resp = json.loads(self.ws.send.call_args[0][0])
        self.assertTrue(resp)

    def test_step(self):
        instance_id = self.make_env(env_path)
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

        api.close(self.ws, instance_id)

    def test_observation_space(self):
        instance_id = self.make_env(env_path)
        env = api.lookup_env(instance_id)

        api.observation_space(self.ws, instance_id)
        info = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(info['name'], 'Box')
        self.assertEqual(info['shape'], list(env.observation_space.shape))
        self.assertEqual(info['low'], env.observation_space.low.tolist())
        self.assertEqual(info['high'], env.observation_space.high.tolist())

        api.close(self.ws, instance_id)

    def test_action_space(self):
        instance_id = self.make_env(env_path)
        env = api.lookup_env(instance_id)

        api.action_space(self.ws, instance_id)
        info = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(info['name'], 'Discrete')
        self.assertEqual(info['n'], env.action_space.n)

        api.close(self.ws, instance_id)

    def test_action_sample(self):
        instance_id = self.make_env(env_path)
        env = api.lookup_env(instance_id)

        api.action_sample(self.ws, instance_id)
        action = json.loads(self.ws.send.call_args[0][0])

        self.assertEqual(np.array(action).shape, env.action_space.shape)

        api.close(self.ws, instance_id)

if __name__ == '__main__':
    unittest.main()
