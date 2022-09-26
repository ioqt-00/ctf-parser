import argparse
import logging
from typing import Dict
import requests
from pathlib import Path

import zmq

from framework import list_, select, configure, flag, create_ctf, show
from framework.classes import Ctf, Challenge
from utils.other import loadconfig

#########################################################################################

class Context():
    challenge_dict: Dict[str, Challenge] = {}
    ctf_dict: Dict[str, Ctf] = {}

    ctf_name: str = ""
    flag_format: str = ""

    selected_ctf: Ctf = None
    selected_challenge: Challenge = None

    rootpath = Path(__file__).resolve().parent

    request_session = requests.Session()
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
    if cmd == "createCTF":
        create_ctf(CTX, args)
    elif cmd == "list" or cmd == "ls":
        list_(CTX, args)
    elif cmd == "select" or cmd == "cd":
        select(CTX, args)
    elif cmd == "config":
        configure()
    elif cmd == "flag":
        flag(CTX, args)
    elif cmd == "show":
        show(CTX, args)
    else:
        CTX.send(f"Command not found: {cmd}")
    CTX.send("EOL")

#############################################################################################

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
                description='This tools is used to create automatically discord threads by'\
                            'scraping ctfd plateform and collecting name, category,'\
                            'description and points of challenges.'
            )
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    format_ = "%(levelname)s %(asctime)s %(message)s"
    logging.basicConfig(format=format_, datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    context = zmq.Context()
    SOCKET = context.socket(zmq.PAIR)
    SOCKET.bind('tcp://127.0.0.1:5555')
    CTX = Context()
    loadconfig(CTX)
    while True:
        try:
            msg = CTX.recv()
            if msg != "":
                cmd_args = msg.split()
                cmd = cmd_args[0].strip()
                args = cmd_args[1:]
                main_switch(cmd, args)
        except Exception as e:
            import traceback
            res = traceback.format_exception(e)
            CTX.send("".join(res))
            CTX.send("EOL")
        except SystemExit:
            CTX.send("EOL")
