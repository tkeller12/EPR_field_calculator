import socket
import time 

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8023)
sock.connect(server_address)


def send_message(message, convert:bool = True, request:bool = False): 
    if message[-1] != '\n':
        message += '\n'
    sock.send(message.encode('utf-8'))
    time.sleep(0.2)
    data = sock.recv(4096)

    if convert: 
        data = data.decode('utf-8')
        if request:
            data = data.split('=')[1]
            data = data.split('\r\n')[0]
            if data in ['True', 'False']:
                return eval(data)
            else:
                if '.' in data:
                    try:
                        data = float(data)
                        return data
                    except:
                        return data
                else:
                    try: 
                        data = int(data)
                        return data
                    except:
                        return data
    return data

def freq():
    data = send_message(".spec.BRIDGE.Frequency")
    print('data',data)

    try:
        freq = float(data.split('=')[-1]) / 1e9
        print('freq',freq)
        return freq
    except:
        return None
def if_freq():
    data = send_message(".spec.AWG.Frequency")
    print('data',data)

    try:
        freq = float(data.split('=')[-1]) / 1e9
        print('freq',freq)
        return freq
    except:
        return None

