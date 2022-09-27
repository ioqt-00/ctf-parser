import os
import zmq

#############################################################################################

if __name__ == '__main__':
    os.makedirs('ctfd', exist_ok=True)
 
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect('tcp://127.0.0.1:5555')
    socket.send_string("reset")
    invite = socket.recv_string()
    print(invite, end="")
    while True:
        invite = socket.recv_string()
        print(invite, end="")
        cmd = input("")
        socket.send_string(cmd.strip())
        ended = False
        while not ended:
            msg = socket.recv_string()
            if msg == "EOL":
                ended = True
            else:
                print(msg)
