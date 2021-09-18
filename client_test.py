import socketio

URL = 'http://localhost:8000'

sio = socketio.Client()

sio.connect(URL)


def callback_fn(evt_name):
    def callback(*args, **kwargs):
        print(f'EVT {evt_name}: Got Callback: args={args}, kwargs={kwargs}')

    return callback


@sio.event
def start(*args):
    print(f'EVENT START, data: {args}')


@sio.event
def error(*args):
    print(f'EVENT ERROR, data: {args}')


@sio.event
def move(*args):
    print(f'EVENT MOVE, data: {args}')


while 1:
    evt = input('Input name of event to send: ')
    datas = []
    while 1:
        data_str = input(f'Input data of event to send (or nothing to stop) (arg #{len(datas)+1}): ')
        if len(data_str) == 0:
            break

        try:
            datas.append(eval(data_str))
        except Exception as e:
            print('EXCEPTION:', e, 'Try again')

    sio.emit(evt, tuple(datas), callback=callback_fn(evt))
    print('Emitted event')
