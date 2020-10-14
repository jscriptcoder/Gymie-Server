import json
import eventlet
from eventlet import wsgi, websocket
from gymie.api import public
from gymie.exceptions import *


#####################################
# WebSocket Server API and Handlers #
#####################################

def message_handle(ws, message):
    """This function will process the message received by the client
    
    Args:
        ws (WebSocket): socket for communication with the client
        message (str): JSON string coming from the client
    
    Raises:
        json.JSONDecodeError: 
            there was a problem decoding the JSON string
        KeyError: 
            there was a problem with the parameters sent by the client
        TypeError: 
            there was a problem with the parameters sent by the client
        InstanceNotFound: 
            instance id is not in the dictionary of envs
        EnvironmentMalformed:
            wrong environment's id
        EnvironmentNotFound:
            environment's id is not registered
        WrongAction:
            there was a problem executing the action on the environment
        Exception:
            there was an unknonwn error
    """
    try:
        data = json.loads(message)
        method = data['method']
        params = data['params']
    except json.JSONDecodeError:
        ws.close((1003, 'Message `{}` is invalid'.format(message)))
    except KeyError:
        keys = str(list(data.keys()))
        ws.close((1003, 'Message keys {} are missing or invalid'.format(keys)))
    else:
        try:
            public[method](ws, **params)
        except KeyError:
            ws.close((1007, 'Method `{}` not found'.format(method)))
        except TypeError:
            ws.close((1007, 'Parameters `{}` are wrong'.format(data['params'])))
        except InstanceNotFound as instance_id:
            ws.close((1007, 'Instance `{}` not found'.format(instance_id)))
        except EnvironmentMalformed as env_id:
            ws.close((1007, 'Environment `{}` is malformed'.format(env_id)))
        except EnvironmentNotFound as env_id:
            ws.close((1007, 'Environment `{}` not found'.format(env_id)))
        except WrongAction as action:
            ws.close((1007, 'Action `{}` is wrong'.format(action)))
        except Exception as err:
            ws.close((1007, 'Unknonwn error: {}'.format(err)))

@websocket.WebSocketWSGI
def gym_handle(ws):
    """This function handles socket communication
    
    Args:
        ws (WebSocket): socket for communication with the client
    """
    while True:
        message = ws.wait()
        if message is None: 
            break
        message_handle(ws, message)

def dispatch(environ, start_response):
    """WSGI application function

    Args:
        environ: 
            additional parameters that go into the environ dictionary of every request
        start_response:
            function that sends a http response to the client
    """
    if environ['PATH_INFO'] == '/gym':
        return gym_handle(environ, start_response)
    else:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Gymie is running...']

def start(host='0.0.0.0', port=5000):
    """Starts the server

    Args:
        host (str): default value '0.0.0.0'
        port (int): default value 5000
    """
    try:
        listener = eventlet.listen((host, port), reuse_port=False)
    except OSError as err:
        print(f'Address http://{host}:{port} already in use')
    else:
        wsgi.server(listener, dispatch)
