#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: ioqt

# pylint: disable=redefined-outer-name

"""main function of server, will communicate with a client and command the execution of
info gathering, parsing & basic analysis"""

from typing import Dict
from pathlib import Path
import logging
import argparse
import json

from flask import Flask, request, jsonify
import requests

from framework.utils import not_implemented
from framework.classes import Ctf, Challenge
from framework import list_, select, configure, flag, create_ctf, show, update, auth
from utils.other import loadconfig

DEBUG = False
ENDPOINT = "ctfd"

app = Flask(__name__)

class Context():
    """Main context of the server, will be passed to submodules to handle the communication
    with the user"""
    def __init__(self):
        self.endpoint = ENDPOINT
        self.json = {"msg":""}

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

    def reset(self):
        logging.debug("Resetting server")
        self.__init__()

    def send(self, msg):
        self.json["msg"] += f"{msg}\n"

    def flush(self):
        res = self.json
        self.json = {"msg":""}
        return res

    def set_data(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        msg = data.get("msg","")
        msg = self.json["msg"] + msg
        self.json = data
        self.json["msg"] = msg

@app.route("/")
def index():
    return "Hey pal, this is ctfd-parser server"

@app.route("/create-ctf")
def launch_create_ctf():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    create_ctf(CTX, args)
    return CTX.flush()

@app.route("/list")
def launch_list():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    list_(CTX, args)
    return CTX.flush()

@app.route("/select")
def launch_select():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    select(CTX, args)
    return CTX.flush()

@app.route("/config")
def config():
    return not_implemented()

@app.route("/flag")
def launch_flag():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    flag(CTX, args)
    return CTX.flush()

@app.route("/show")
def launch_show():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    show(CTX, args)
    return CTX.flush()

@app.route("/reset")
def reset():
    CTX.reset()
    loadconfig(CTX)
    return {"msg":"Context reset"}

@app.route("/auth")
def launch_auth():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    auth(CTX, args)
    return CTX.flush()

@app.route("/update")
def launch_update():
    if request.json is not None:
        args = json.loads(request.json)
    else:
        args = {}
    update(CTX, args)
    return CTX.flush()

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

    CTX = Context()
    if args.debug:
        CTX.DEBUG = True

    loadconfig(CTX)

    app.run()
