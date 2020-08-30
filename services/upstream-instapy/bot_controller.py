import os
import json
import requests
import websocket
from websocket import create_connection
import sys
import time

# constants
AUTH_ENDPOINT = os.getenv('AUTH_ENDPOINT', 'https://auth.instapy.io')
CONFIG_ENDPOINT = os.getenv('CONFIG_ENDPOINT', 'https://config.instapy.io')
SOCKET_ENDPOINT = os.getenv('SOCKET_ENDPOINT', 'wss://socket.instapy.io')
INSTAPY_USER = os.getenv('INSTAPY_USER')
INSTAPY_PASSWORD = os.getenv('INSTAPY_PASSWORD')
IDENT = os.getenv('IDENT')

if not IDENT:
    print('IDENT not provided')
    sys.exit(1)

# globals
PROCESS = None
TOKEN = None
HANDLERS = {}
NAMESPACE = None
SETTING = None
OPERATION = False


def get_token(username, password):
    payload = {'username': username, 'password': password}

    url = AUTH_ENDPOINT + '/login'
    print(f'authenticate {username} to {url} ...')

    response = requests.post(url, data=payload)
    response = response.json()
    if 'error' in response:
        print(response['error'])
        sys.exit()

    print(f'logged in with user: {username}')
    return response['token']


if __name__ == '__main__':
    param = sys.argv[1]

    operation = True if param == 'start' else False
    NAMESPACE = IDENT

    print('bot-controller: {0}, action: {1}'.format(IDENT, param))

    username = INSTAPY_USER
    password = INSTAPY_PASSWORD

    TOKEN = get_token(username, password)
    header = {'Authorization': f'Bearer {TOKEN}'}

    socket = create_connection(SOCKET_ENDPOINT, header=header)

    socket.send(
        json.dumps(
            {'handler': 'bot', "start": operation, 'namespace': NAMESPACE, 'setting': IDENT, 'bot': "{0}-bot".format(IDENT)}
        )
    )
    socket.close()
