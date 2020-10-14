# Gymie - Server

WebSocket server that exposes an API to train AI agents on [OpenAI Gym](https://gym.openai.com/) and gym-api like Environments such as [Gym Retro](https://openai.com/blog/gym-retro/) or [Unity ML-Agents](https://unity3d.com/machine-learning/), this last one with the help of [gym wrapper](https://github.com/Unity-Technologies/ml-agents/tree/master/gym-unity)

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
pip install -e .
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
