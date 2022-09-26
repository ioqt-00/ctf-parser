import argparse
import logging
from urllib.parse import urlparse, urljoin
import requests

import zmq

from helpers.ctfdhelper import utils, create_ctf
from framework import list_, select, configure, flag

##########################################################################################################################

class Context():
    challenge_list = {}
    all_ctf = []
    ctf_name = ""
    formatflag = ""
    session = requests.Session()
    CONFIG = {
        'user': None,
        'password': None,
        'base_url': None,
        'token': None,
    }

    def send(self, msg):
        SOCKET.send_string(msg)

    def recv(self):
        return SOCKET.recv_string()

def main_switch(cmd, args) -> None:
    global CONFIG
    if cmd == "createCTF":
        CONFIG = create_ctf(CTX, args, CONFIG)
    elif cmd == "list":
        list_(CTX, args)
    elif cmd == "select":
        select(CTX, args)
    elif cmd == "config":
        configure(CTX, args)
    elif cmd == "flag":
        flag(CTX, args)
    else:
        CTX.send(f"Command not found: {cmd}")
    CTX.send(f"EOL")

#############################################################################################

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='This tools is used to create automatically discord threads by scraping ctfd plateform and collecting name , category , description and points of challenges.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
  
    format = "%(levelname)s %(asctime)s %(message)s"
    logging.basicConfig(format = format, datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    context = zmq.Context()
    SOCKET = context.socket(zmq.PAIR)
    SOCKET.bind('tcp://127.0.0.1:5555')
    CTX = Context()
    while True:
        try:
            msg = CTX.recv()
            if msg != "":
                cmd_args = msg.split()
                cmd = cmd_args[0].strip()
                args = cmd_args[1:]
                res = main_switch(cmd, args)
        except Exception as e:
            import traceback
            res = traceback.format_exception(e)
            CTX.send("".join(res))       
            CTX.send("EOL")     
        except SystemExit:
            CTX.send("EOL")