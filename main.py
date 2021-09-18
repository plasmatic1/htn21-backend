import logging
import colorama
import coloredlogs
import socketio
import uuid

import util

from aiohttp import web

DEBUG = True
LOG_FORMAT = '[%(asctime)s/%(name)s] %(levelname)s %(message)s'
TIME_FORMAT = '%H:%M:%S'

GAME_SIZE = 8

colorama.init()
coloredlogs.install(fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
if DEBUG:
    coloredlogs.set_level(logging.DEBUG)

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins=['*'])
app = web.Application()
sio.attach(app)


# Game globals
class Game:
    def __init__(self, sids, grid, ready):
        self.sids = sids
        self.grid = grid
        self.ready = ready


cons: dict[str, Game] = {}
game_uid: dict[str, str] = {}


async def err(sid, msg):
    await sio.emit('error', msg, to=sid)
    logging.warning(f'Error: User {sid} got error {msg}')


@sio.event
def connect(sid, environ):
    logging.info(f'Connection: {sid}')

    return sid


@sio.event
def disconnect(sid):
    logging.info(f'Disconnection: {sid}')


@sio.event
def create(sid):
    gid = str(uuid.uuid4())

    logging.info('eventJSDF OIJSDOFIJSOIFJSIOFJSOFJSDFIODFJ')

    assert gid not in cons
    cons[gid] = Game([], util.generate_map(GAME_SIZE), False)

    logging.info(f'User {sid} requests new game {gid}')
    logging.debug(f'Grid: {cons[gid].grid}')

    return gid


@sio.event
async def get(sid, uid):
    if uid not in cons:
        await err(sid, f'Game {uid} does not exist')
        return

    if len(cons[uid].sids) >= 2:
        await err(sid, f'Game {uid} already full')
        return

    cons[uid].sids.append(sid)
    game_uid[sid] = uid

    if len(cons[uid].sids) == 2:
        cons[uid].ready = True
        for player_sid in cons[uid].sids:
            await sio.emit('start', to=player_sid)

    logging.info(f'User {sid} requested game {uid}, game now has users {cons[uid].sids}, ready state: {cons[uid].ready}')

    return cons[uid].grid


@sio.event
async def move(sid, x, y):
    if sid not in game_uid:
        await err(sid, f'User {sid} not in game')
        return

    assert game_uid[sid] in cons

    if not cons[game_uid[sid]].ready:
        await err(sid, f'Game {game_uid[sid]} not ready yet')
        return

    logging.info(f'User {sid} sent move({x}, {y}) to game {game_uid[sid]}')

    for player_sid in cons[game_uid[sid]].sids:
        if player_sid != sid:
            await sio.emit('move', (x, y), to=player_sid)


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8000)
