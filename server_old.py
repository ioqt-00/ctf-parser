#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: ioqt

# pylint: disable=redefined-outer-name

"""main function of server, will communicate with a client and command the execution of
info gathering, parsing & basic analysis"""

import argparse
import logging
from typing import Dict
from pathlib import Path

import zmq
import requests

from framework import list_, select, configure, flag, create_ctf, show, update, auth
from framework.classes import Ctf, Challenge
from utils.other import loadconfig

#########################################################################################

class Context():
    """Main context of the server, will be passed to submodules to handle the communication
    with the user"""
    def __init__(self):
        self.DEBUG = False
        self.endpoint = "ctfd"

        self.challenge_dict: Dict[str, Challenge] = {}
        self.ctf_dict: Dict[str, Ctf] = {}

        self.ctf_name: str = ""
        self.flag_format: str = ""

        self.selected_ctf: Ctf = None
        self.selected_challenge: Challenge = None

        self.rootpath = Path(__file__).resolve().parent

        self.request_session = requests.Session()
        self.request_config = {
            'user': None,
            'password': None,
            'base_url': None,
            'token': None,
        }

        self.socket = SOCKET

    def send(self, msg):
        SOCKET.send_string(msg)

    def recv(self):
        return SOCKET.recv_string()

    def reset(self):
        logging.debug("Resetting server")
        self.__init__()


def main_switch(cmd, args) -> None:
    if cmd == "createCTF":
        create_ctf(CTX, args)
    elif cmd in set(["list","ls"]):
        list_(CTX, args)
    elif cmd in set(["select","cd"]):
        select(CTX, args)
    elif cmd == "config":
        configure()
    elif cmd == "flag":
        flag(CTX, args)
    elif cmd == "show":
        show(CTX, args)
    elif cmd == "resetA":
        CTX.reset()
        loadconfig(CTX)
        return
    elif cmd == "auth":
        auth(CTX, args)
    elif cmd == "update":
        update(CTX, args)
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
    parser.add_argument("--debug", action='store_true', help="Debug flag")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    format_ = "%(levelname)s %(asctime)s %(message)s"
    logging.basicConfig(format=format_, datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    zmq_context = zmq.Context()
    SOCKET = zmq_context.socket(zmq.PAIR)
    SOCKET.bind('tcp://127.0.0.1:5555')
    CTX = Context()
    if args.debug:
        CTX.DEBUG = True
    loadconfig(CTX)
    while True:
        try:
            CTX.send("server > ")
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
