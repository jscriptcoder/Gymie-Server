# Gymie - Server

![PyPI](https://img.shields.io/pypi/v/gymie)

WebSocket server that exposes an API to train AI agents on [OpenAI Gym](https://gym.openai.com/) and gym-api like environments such as [Gym Retro](https://openai.com/blog/gym-retro/) or [Unity ML-Agents](https://unity3d.com/machine-learning/), this last one with the help of [gym wrapper](https://github.com/Unity-Technologies/ml-agents/tree/master/gym-unity)

## Content of this document
- [Installation](#installation)
- [How to start the server](#how-to-start-the-server)
- [API and how to consume it](#api-and-how-to-consume-it)
  - [List of methods exposed to the client](list-of-methods-exposed-to-the-client)
    - [make](#make)
    - [step](#step)
    - [reset](#reset)
    - [close](#close)
    - [observation_space](#observation_space)
    - [action_space](#action_space)
    - [action_sample](#action_sample)
  - [Programmatic API](#programmatic-api)
    - [@override](#override)
    - [start](#start)
- [Testing Gymie](#testing-gymie)
- [Licence](#license)

## Installation

Gymie can be installed using:

```bash
$ pip install gymie
```

or by cloning the [repo](https://github.com/jscriptcoder/Gymie-Server) and pip-installing in editable mode from the folder:

```bash
$ git clone https://github.com/jscriptcoder/Gymie-Server.git
Cloning into 'Gymie-Server'...
...

$ cd Gymie-Server/
$ pip install -e .
Obtaining file:///path/to/Gymie-Server
...
Successfully installed gymie
```

## How to start the server

You can start the server from the command line:

```bash
$ python -m gymie --host 0.0.0.0 --port 5000
(84581) wsgi starting up on http://0.0.0.0:5000
```

or programmatically:

```python
import gymie

gymie.start('localhost', 9000)
```

## API and how to consume it

A client can communicate with Gymie via JSON, with the following format:
```json
{
  "method": "api_method_name",
  "params": {
    "param1": "string",
    "param2": 6,
    "param3": true,
    "param4": []
  }
}
```

### List of methods exposed to the client
- <a name="make">`make`</a>: Instantiates an environment. 
 ```js
 // Params:
 {
   "env_id": "CartPole-v1",
   "seed":   0 // optional
 }
 
 // Response:
 {
   "instance_id": "unique-id"
 }
 ```
- <a name="step">`step`</a>: Performs a step on the environment. 
 ```js
 // Params:
 {
   "instance_id": "instance-id"
   "action":      [1, 0, 1] // MultiBinary action
 }
 
 // Response:
 [
   [...], // next state
   -2.0,  // reward
   false, // done
   {...}, // info
 ]
 ```
- <a name="reset">`reset`</a>: Resets the environment.
 ```js
 // Params:
 {
   "instance_id": "instance-id"
 }
 
 // Response:
 [...] // initial state
 ```
- <a name="close">`close`</a>: Closes the environment.
 ```js
 // Params:
 {
   "instance_id": "instance-id"
 }
 
 // Response:
 true
 ```
- <a name="observation_space">`observation_space`</a>: Generates a dictionary with observation space info.
 ```js
 // Params:
 {
   "instance_id": "instance-id"
 }
 
 // Response for Discreate observation space:
 {
   "name": "Discreate",
   "n":    4
 }
 
 // Response for Box (Continuous) observation space:
 {
   "name":  "Box",
   "shape": [3],
   "low":   [-5, -5, -5],
   "high":  [5, 5, 5]
 }
 
 // Response for MultiBinary observation space:
 {
   "name":  "MultiBinary",
   "n":     5,
   "shape": [5]
 }
 
 // TODO MultiDiscrete
 ```
- <a name="action_space">`action_space`</a>: Generates a dictionary with action space info.
 ```js
 // Params:
 {
   "instance_id": "instance-id"
 }
 
 // Response for Discreate actions:
 {
   "name": "Discreate",
   "n":    4
 }
 
 // Response for Box (Continuous) actions:
 {
   "name":  "Box",
   "shape": [2],
   "low":   [-1, -1],
   "high":  [1, 1]
 }
 ```
 - <a name="action_sample">`action_sample`</a>: Generates a random action.
```js
// Params:
{
 "instance_id": "instance-id"
}

// Response for Discrete actions:
2

// Response for Continuous actions:
[1.52, -3.67]
```
 
### Programmatic API

- <a name="override">`@override`</a>: Decorator to override internal functionality. It takes a string, function's name, as an argument. This is useful if we want to use different gym-like wrappers. For example, both Gym Retro and Unity ML-Agents have different ways to instantiate an environment. You can take a look at the tests to see how it's done for [Gym Retro](tests/test_gymie_retro.py) and [Unity ML-Agents](https://github.com/jscriptcoder/Gymie-Server/blob/main/tests/test_gymie_unity.py) (with the help of [gym-unity](https://github.com/Unity-Technologies/ml-agents/tree/master/gym-unity)). At the moment there are two internal functions that can be overriden, `get_env` and `process_step`.

#### Signature:
```python
def override(func_name: str) -> Callable
````

#### How to use:
```python
import retro
from gymie import override
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.environment import UnityEnvironment, UnityEnvironmentException

@override('get_env')
def retro_get_env(env_id, seed=None):
    """Instantiates a Gym environment"""
    try:
        env = retro.make(game=env_id)
    except FileNotFoundError:
        raise EnvironmentNotFound
    else:
        if seed: 
            env.seed(seed)

        return env


@override('process_step')
def unity_process_step(step):
    """Does some processing of the step"""
    observation, reward, done, info = step
    return observation.tolist(), float(reward), done, {}
```

- <a name="start">`start`</a>: This function takes two arguments, host and port, and starts the server, listening on `ws://host:port`

#### Signature:
```python
def start (host: str = '0.0.0.0', port: int = 5000) -> None
```

#### How to use:
```python
import gymie

gymie.start('localhost', 8080)
```

## Testing Gymie

You can run all the tests by executing `run_tests.sh` script:
```bash
$ ./run_tests.sh
```

In order to run [`test_gymie_retro.py`](tests/test_gymie_retro.py) you need to have [gym-retro](https://pypi.org/project/gym-retro/) package installed. For [`tests/test_gymie_unity.py`](tests/test_gymie_unity.py), you need [mlagents-envs](https://pypi.org/project/mlagents-envs/) and [gym-unity](https://pypi.org/project/gym-unity/). 

## License

[MIT License](LICENSE) - Copyright (c) 2020 Francisco Ramos
