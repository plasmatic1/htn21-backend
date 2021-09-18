import logging
import colorama
import coloredlogs
import socketio
import uuid
import collections

import util

from typing import dict

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
Game = collections.namedtuple('Game', 'sids grid ready')
cons: dict[str, Game] = {}
game_uid: dict[str, str] = {}


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
    cons[gid] = Game([], util.generate_map(GAME_SIZE), False)

    return gid


@sio.event
def get(sid, uid):
    if uid not in cons:
        sio.emit('error', f'Game {uid} does not exist', room=sid)
        return

    if len(cons[uid].sids) >= 2:
        sio.emit('error', f'Game {uid} already full', room=sid)
        return

    cons[uid].sids.append(sid)
    game_uid[sid] = uid

    if len(cons[uid].sids) == 2:
        cons[uid].ready = True

    return cons[uid].grid


@sio.event
def move(sid, x, y):
    if sid not in game_uid:
        sio.emit('error', f'User {sid} not in game')
        return