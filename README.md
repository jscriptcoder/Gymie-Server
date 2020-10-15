# Gymie - Server

WebSocket server that exposes an API to train AI agents on [OpenAI Gym](https://gym.openai.com/) and gym-api like Environments such as [Gym Retro](https://openai.com/blog/gym-retro/) or [Unity ML-Agents](https://unity3d.com/machine-learning/), this last one with the help of [gym wrapper](https://github.com/Unity-Technologies/ml-agents/tree/master/gym-unity)

## Contents of this document
- [Installation](#installation)
- [How to start the server](#how-to-start-the-server)
- [API and how to consume it](#api-and-how-to-consume-it)
  - make
  - step
  - reset
  - close
  - observation_space
  - action_space
  - action_sample
  

## Installation

Gymie can be installed using:

```
$ pip install gymie
```

or by cloning the [repo](https://github.com/jscriptcoder/Gymie-Server) and pip-installing in editable mode from the folder:

```
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

```
$ python gymie --host 0.0.0.0 --port 5000
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

#### List of methods:
- `make`: Instantiates an environment. 
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
- `step`: Performs a step in the environment. 
 ```js
 // Params:
 {
   "instance_id": "instance-id"
   "action":      "CartPole-v1"
 }
 
 // Response:
 [
   [...], // next state
   -2.0,  // reward
   false, // done
   {...}, // info
 ]
 ```
- `reset`: Resets the environment.
 ```js
 // Params:
 {
   "instance_id": "instance-id"
 }
 
 // Response:
 [...] // initial state
 ```
- `close`: Closes the environment.
 ```js
 // Params:
 {
   "instance_id": "instance-id"
 }
 
 // Response:
 true
 ```
- `observation_space`: Generates a dictionary with abservation space info.
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
   "shape": [5],
   "low":   [0],
   "high":  [1]
 }
 
 // TODO MultiDiscrete
 ```
- `action_space`: Generates a dictionary with action space info.
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
   "low":   [-1, -1, -1],
   "high":  [1, 1, 1]
 }
 ```
 - `action_sample`: Generates a random action.
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
