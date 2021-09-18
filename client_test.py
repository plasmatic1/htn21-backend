import socketio

URL = 'http://localhost:8000'

sio = socketio.Client()

sio.connect(URL)

def callback_fn(evt_name):
    def callback(*args, **kwargs):
        print(f'EVT {evt_name}: Got Callback: args={args}, kwargs={kwargs}')

    return callback


while 1:
    evt = input('Input name of event to send: ')
    # datas = []
    # while 1:
    # data_str = input(f'Input data of event to send (or nothing to stop) (arg #{len(datas)+1}): ')
    # if len(data_str) == 0:
    #     break
    # datas.append(eval(data_str))

    data = eval(input('Input event data: '))

    sio.emit(evt, data, callback=callback_fn(evt))
    print('Emitted event')