import gym
import json
import uuid
import numpy as np
from gymie.exceptions import *


# Dictionary containing a list of pairs unique-id/environment
envs = {}

# Exposed API accessible via string key
public = {}


##############
# Decorators #
##############

def public_api(fn):
    """Decorator that populates the dictionary of public api
    
    Args:
        fn: api function
    """
    public[fn.__name__] = fn
    return fn

def override(func_name):
    """Decorator that overrides internal functionality
    giving the possibility of using different Gym-like env wrappers
    such as Unity ML-Agents or Gym Retro.
    
    Currently there are two functions to override:
    1. get_env: instantiates a Gym environment
    2. process_step: does some processing of the environment step

    Args:
        func_name (str): function to override
    
    Raises:
        AssertionError: wrong function to override
    """
    assert func_name in ['get_env', 'process_step'], \
        'Error overriding. Functions available: `get_env`, `process_step`'
    
    def inner_override(fn):
        globals()[func_name] = fn
        return fn
    
    return inner_override


#############
# API logic #
#############

def get_env(env_id, seed=None):
    """Instantiates a Gym environment
    
    Args:
        env_id (str): environment id
        seed (int): optional; initial seed for randomnes
    
    Returns:
        Gym environment
    
    Raises:
        EnvironmentNotFound: environment env_id does not exist
        EnvironmentMalformed: env_id is not correct
    """
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

def process_step(step):
    """Does some processing of the step
    
    Args:
        step (tuple(np.array(float), float, bool, dict)):
            returns by environment.step method
    
    Returns:
        Processed step
    """
    observation, reward, done, info = step
    return observation.tolist(), reward, done, info

def lookup_env(instance_id):
    """Looks up an environment based on instance id

    Args:
        instance_id (str): given instance id
    
    Returns:
        Gym environment
    
    Raises:
        InstanceNotFound: instance isn't found in the dictionary
    """
    try:
        return envs[instance_id]
    except KeyError:
        raise InstanceNotFound(instance_id)

@public_api
def make(ws, env_id, **kwargs):
    """API method. Instantiates an environment
    and sends the instance id to the client

    Args:
        ws (WebSocket): socket where to send stuff
        env_id (str): environment id
    """
    env = get_env(env_id, **kwargs)
    instance_id = uuid.uuid4().hex
    envs[instance_id] = env
    ws.send(instance_id)

@public_api
def step(ws, instance_id, action, render=False):
    """API method. Performs a step in the environment
    and sends the result to the client

    Args:
        ws (WebSocket): socket for communication with the client
        instance_id (str): env's instance id where to execute the step
        action (int|list): action to send to the environment
        render (bool): optional; whether or not to render the scene
    
    Raises:
        WrongAction: there was an issue executing the action
    """
    env = lookup_env(instance_id)

    if render: 
        env.render()

    try:
        step = env.step(action)
    except:
        raise WrongAction(str(action))
    else:
        ws.send(json.dumps(process_step(step)))

@public_api
def reset(ws, instance_id):
    """API method. Resets the environment
    and sends the initial state to the client

    Args:
        instance_id (str): instance id of the env to reset
    """
    state = lookup_env(instance_id).reset()
    ws.send(str(state.tolist()))

@public_api
def close(ws, instance_id):
    """API method. Closes the environment
    and sends confirmation to the client

    Args:
        instance_id (str): instance id of the env to close
    """
    lookup_env(instance_id).close()
    del envs[instance_id]

    is_closed = instance_id not in envs
    ws.send(json.dumps(is_closed))

def space_info(space):
    """Returns information about the space in a dictionary

    Args:
        space (Space): space to extract info from
    
    Returns:
        Dictionary with information about the space such as 
        type of space, shape, low and high values, etc...
    """
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
        info['shape'] = space.shape # TODO: does it make sense to return this?
    elif name == 'MultiDiscrete':
        # TODO: finish this one.
        pass

    return info

@public_api
def observation_space(ws, instance_id):
    """API method. Generates a dictionary with space info 
    and sends it to the client

    Args:
        instance_id (str): environment's instance id
    """
    space = lookup_env(instance_id).observation_space
    info = space_info(space)
    ws.send(json.dumps(info))

@public_api
def action_space(ws, instance_id):
    """API method. Generates a dictionary with space info 
    and sends it to the client

    Args:
        instance_id (str): environment's instance id
    """
    space = lookup_env(instance_id).action_space
    info = space_info(space)
    ws.send(json.dumps(info))

@public_api
def action_sample(ws, instance_id):
    """API method. Generates a random action
    and sends it to the client

    Args:
        instance_id (str): environment's instance id
    """
    env = lookup_env(instance_id)
    action = env.action_space.sample()
    if hasattr(action, 'tolist'):
        action = action.tolist()
    ws.send(str(action))
