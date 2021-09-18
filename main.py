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
Game = collections.namedtuple('Game', 'sids grid ready')
cons: dict[str, Game] = {}
game_uid: dict[str, str] = {}


def err(sid, msg):
    sio.emit('error', msg, room=sid)
    logging.warning(f'Error: User {sid} got error {msg}')


@sio.event
def connect(sid, environ):
    logging.info(f'Connection: {sid}')


@sio.event
def disconnect(sid):
    logging.info(f'Disconnection: {sid}')


@sio.event
def create(sid):
    gid = str(uuid.uuid4())

    assert gid not in cons
    cons[gid] = Game([], util.generate_map(GAME_SIZE), False)

    logging.info(f'User {sid} requests new game {gid}')
    logging.debug(f'Grid: {cons[gid].grid}')

    return gid


@sio.event
def get(sid, uid):
    if uid not in cons:
        err(sid, f'Game {uid} does not exist')
        return

    if len(cons[uid].sids) >= 2:
        err(sid, f'Game {uid} already full')
        return

    cons[uid].sids.append(sid)
    game_uid[sid] = uid

    if len(cons[uid].sids) == 2:
        cons[uid].ready = True
        for player_sid in cons[uid].sids:
            sio.emit('start', room=player_sid)

    logging.info(f'User {sid} requested game {uid}, game now has users {cons[uid].sids}, ready state: {cons[uid].ready}')

    return cons[uid].grid


@sio.event
def move(sid, x, y):
    if sid not in game_uid:
        err(sid, f'User {sid} not in game')
        return

    assert game_uid[sid] in cons

    if not cons[game_uid[sid]].ready:
        err(sid, f'Game {game_uid[sid]} not ready yet')
        return

    logging.info(f'User {sid} sent move({x}, {y}) to game {game_uid[sid]}')

    for player_sid in cons[game_uid[sid]].sids:
        if player_sid != sid:
            sio.emit('move', {'x': x, 'y': y}, room=player_sid)