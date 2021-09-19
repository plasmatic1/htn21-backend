import logging
import colorama
import coloredlogs
import socketio
import uuid
import threading
import time

import util

from aiohttp import web
from datetime import datetime, timedelta
from sanic import Sanic

DEBUG = True
LOG_FORMAT = '[%(asctime)s/%(name)s] %(levelname)s %(message)s'
TIME_FORMAT = '%H:%M:%S'

GAME_SIZE = 6
AFK_DURATION = timedelta(minutes=5)

colorama.init()
coloredlogs.install(fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
if DEBUG:
    coloredlogs.set_level(logging.DEBUG)

sio = socketio.AsyncServer(async_mode='sanic', cors_allowed_origins=[])
app = Sanic(name='htn21-backend')
app.config['CORS_AUTOMATIC_OPTIONS'] = True
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
sio.attach(app)


# Game globals
class Game:
    def __init__(self, sids, grid, ready):
        self.sids: list[str] = sids
        self.grid: list[list[str]] = grid
        self.ready: bool = ready
        self.last_action = datetime.now()


cons: dict[str, Game] = {}
game_uid: dict[str, str] = {}


async def err(sid, msg):
    await sio.emit('error', msg, to=sid)
    logging.warning(f'Error: User {sid} got error {msg}')


def delete_game(uid):
    logging.info(f'Deleting game {uid}...')

    for player_sid in cons[uid].sids:
        if player_sid in game_uid:
            del game_uid[player_sid]

    if uid in cons:
        del cons[uid]


@sio.event
def connect(sid, environ):
    logging.info(f'Connection: {sid}')

    return sid


@sio.event
def disconnect(sid):
    if sid in game_uid:
        uid = game_uid[sid]
        cons[uid].sids.remove(sid)
        if len(cons[uid].sids) == 0:
            delete_game(uid)

    logging.info(f'Disconnection: {sid}')


@sio.event
def create(sid):
    gid = str(uuid.uuid4())[:8]

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

    if cons[uid].ready:
        await err(sid, f'Game {uid} already full/started')
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

    cons[game_uid[sid]].last_action = datetime.now()
    for player_sid in cons[game_uid[sid]].sids:
        if player_sid != sid:
            await sio.emit('move', [x, y], to=player_sid)


### DISCONNECTING THREAD ###
def kick_loop():
    while 1:
        logging.info('Checking kick loop...')
        rem_ids = []
        for k, g in cons.items():
            if datetime.now() - g.last_action > AFK_DURATION:
                rem_ids.append(k)

        for rem_id in rem_ids:
            delete_game(rem_id)

        time.sleep(2 * AFK_DURATION.total_seconds())


th = threading.Thread(target=kick_loop)
th.start()

if __name__ == '__main__':
    app.run('0.0.0.0', 8000)
