import os
import zmq

#############################################################################################

if __name__ == '__main__':
    if not os.path.isdir('ctfd'):
        os.makedirs('ctfd', exist_ok=True) 
    
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect('tcp://127.0.0.1:5555')
    while True:
        cmd = input("> ")
        socket.send_string(cmd.strip())
        ended = False
        while not ended:
            msg = socket.recv_string()
            if msg == "EOL":
                ended = True
            else:
                print(msg)
                socket.send_string("")
