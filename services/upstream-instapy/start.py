from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('instapy.env')


import os
import signal
import subprocess
import platform
import sys
import json
import time
import websocket
import requests
import threading

# constants
AUTH_ENDPOINT = os.getenv('AUTH_ENDPOINT', 'https://auth.instapy.io')
CONFIG_ENDPOINT = os.getenv('CONFIG_ENDPOINT', 'https://config.instapy.io')
SOCKET_ENDPOINT = os.getenv('SOCKET_ENDPOINT', 'wss://socket.instapy.io')
INSTAPY_USER = os.getenv('INSTAPY_USER')
INSTAPY_PASSWORD = os.getenv('INSTAPY_PASSWORD')
IDENT = os.getenv('IDENT')

print('Running instabot version: 1.0.0')

if not IDENT:
    print('IDENT not provided')
    sys.exit(1)

# globals
PROCESS = None
TOKEN = None
HANDLERS = {}
NAMESPACE = None
SETTING = None

# socke stuff
def on_message(ws, message):
    print('received message:', message)
    data = json.loads(message)
    if data['handler'] not in HANDLERS:
        print('could not locate handler:', data['handler'])
        return

    HANDLERS[data['handler']](ws, data)


def on_error(ws, error):
    print('error:', error)


def on_close(ws):
    print('closed socket')


def on_open(ws):
    print('opened socket')
    print('goto instapy.io and take off!')
    global IDENT
    ws.send(json.dumps({'handler': 'register', 'type': 'instapy', 'ident': IDENT}))
    threading.Thread(target=print_status, args=(ws,)).start()


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

def print_status(ws):
    while True:
        time.sleep(10)
        status = get_status(ws, None)
        with open('status', 'w') as f:
            f.write(status)

# utils
def kill():
    global PROCESS
    if not PROCESS:
        return
    if PROCESS.poll() is None:
        print('killing process...')

        if platform.system() == 'Windows':
            PROCESS.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(PROCESS.pid), signal.SIGTERM)

        print('process killed')

    PROCESS = None


def check_process():
    global PROCESS
    if not PROCESS:
        return
    if PROCESS.poll() is not None:
        kill()


# handlers
def get_status(ws, data):
    check_process()
    global PROCESS
    global NAMESPACE
    global SETTING

    status = 'running' if PROCESS else 'stopped'

    if data is None:
        return status

    ws.send(
        json.dumps(
            {
                'handler': 'status',
                'status': status,
                'namespace': NAMESPACE,
                'setting': SETTING,
                'action': 'set',
            }
        )
    )


HANDLERS['status'] = get_status


def start(ws, data):
    check_process()
    global PROCESS
    global TOKEN
    global IDENT
    global NAMESPACE
    global SETTING

    if PROCESS:
        print('process already running. Wont start another one.')
        return

    ienv = os.environ.copy()
    ienv['TOKEN'] = TOKEN
    ienv['NAMESPACE'] = data['namespace']
    NAMESPACE = data['namespace']
    ienv['SETTING'] = data['setting']
    SETTING = data['setting']
    ienv['SOCKET'] = SOCKET_ENDPOINT
    ienv['CONFIG'] = CONFIG_ENDPOINT
    ienv['IDENT'] = IDENT

    if platform.system() == 'Windows':
        PROCESS = subprocess.Popen(
            [sys.executable, 'bot.py'],
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            env=ienv,
        )
    else:
        PROCESS = subprocess.Popen(
            [sys.executable, 'bot.py'], preexec_fn=os.setsid, env=ienv
        )

    print('instapy process started')
    get_status(ws, data)


HANDLERS['start'] = start


def stop(ws, data):
    kill()
    get_status(ws, data)


HANDLERS['stop'] = stop


def reset(ws, data):
    stop(ws, data)
    start(ws, data)


HANDLERS['reset'] = reset


if __name__ == '__main__':
    username = INSTAPY_USER
    password = INSTAPY_PASSWORD

    TOKEN = get_token(username, password)
    header = {'Authorization': f'Bearer {TOKEN}'}

    while True:
        try:
            ws = websocket.WebSocketApp(
                SOCKET_ENDPOINT,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                header=header,
            )

            ws.on_open = on_open
            ws.run_forever(ping_interval=30)
            time.sleep(3)

        except KeyboardInterrupt:
            break
