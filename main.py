import logging
import colorama
import coloredlogs
import socketio
import uuid
import collections

import util

from typing import Dict

DEBUG = True
LOG_FORMAT = '[%(asctime)s/%(name)s] %(levelname)s %(message)s'
TIME_FORMAT = '%H:%M:%S'

GAME_SIZE = 8

colorama.init()
coloredlogs.install(fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
if DEBUG:
    coloredlogs.set_level(logging.DEBUG)

STATIC_FILES = {
    '/static': './static'
}

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=STATIC_FILES)

# Game globals
Game = collections.namedtuple('Game', 'sids grid')
cons : dict[str, Game] = {}


@sio.event
def connect(sid, environ):
    print('Connection:', sid)


@sio.event
def disconnect(sid, environ):
    print('Disconnection:', sid)


@sio.event
def create(sid):
    gid = str(uuid.uuid4())

    assert gid not in cons
    cons[gid] = Game([], util.generate_map(GAME_SIZE))

    return gid


@sio.event
def get(sid, uid):
    if uid not in cons:
        sio.emit('error', f'Game {uid} does not exist', room=sid)
        return

    game = cons[uid]

    if len(game.sids) >= 2:
        sio.emit('error', f'Game {uid} already full', room=sid)
        return


@sio.event
def move(sid, x, y):
