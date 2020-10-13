import gym
import json
import uuid
import numpy as np
from gymie.exceptions import *

##########################
# Environments Container #
##########################

envs = {}


#########################################
# Gym.Env Wrapper Functions and Helpers #
#########################################

def lookup_env(instance_id):
    try:
        return envs[instance_id]
    except KeyError:
        raise InstanceNotFound(instance_id)

def openai_gym_get_env(env_id, seed=None):
    try:
        env = gym.make(env_id)
    except gym.error.UnregisteredEnv:
        raise EnvironmentNotFound(env_id)
    except gym.error.Error:
        raise EnvironmentMalformed(env_id)
    else:
        if seed: 
            env.seed(seed)
        
        return env

# Allows overriding to define other Gym-api like wrappers
defs = { 'get_env': openai_gym_get_env }

def make(ws, env_id, **kwargs):
    env = defs['get_env'](env_id, **kwargs)
    instance_id = uuid.uuid4().hex
    envs[instance_id] = env
    ws.send(instance_id)

def step(ws, instance_id, action, render=False):
    env = lookup_env(instance_id)

    if render: 
        env.render()

    try:
        observation, reward, done, info = env.step(action)
    except:
        raise WrongAction(str(action))
    else:
        ws.send(json.dumps([observation.tolist(), reward, done, info]))

def reset(ws, instance_id):
    state = lookup_env(instance_id).reset()
    ws.send(str(state.tolist()))
    
def close(ws, instance_id):
    lookup_env(instance_id).close()
    del envs[instance_id]

    isClosed = instance_id not in envs
    ws.send(json.dumps(isClosed))

def space_info(space):
    name = space.__class__.__name__
    info = { 'name': name }

    if name in 'Discrete':
        info['n'] = space.n
    elif name == 'Box':
        info['shape'] = space.shape

        # I noticed that numpy.float32 isn't JSON serializable but numpy.float64 is.
        info['low'] = space.low.astype('float64').tolist()
        info['high'] = space.high.astype('float64').tolist()
    elif name == 'MultiBinary':
        info['n'] = space.n
        info['shape'] = space.shape
        info['low'] = [0]
        info['high'] = [1]
    elif name == 'MultiDiscrete':
        pass

    # TODO other shapes

    return info

def observation_space(ws, instance_id):
    space = lookup_env(instance_id).observation_space
    info = space_info(space)
    ws.send(json.dumps(info))

def action_space(ws, instance_id):
    space = lookup_env(instance_id).action_space
    info = space_info(space)
    ws.send(json.dumps(info))

def action_sample(ws, instance_id):
    env = lookup_env(instance_id)
    action = env.action_space.sample()
    if hasattr(action, 'tolist'):
        serialized_action = json.dumps(action.tolist())
    else:
        serialized_action = str(action)
    ws.send(serialized_action)


#########################################
# Exposed API accessible via string key #
#########################################

methods = {
    'make': make,
    'reset': reset,
    'step': step,
    'close': close,
    'observation_space': observation_space,
    'action_space': action_space,
    'action_sample': action_sample
}
