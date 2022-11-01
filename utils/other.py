#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec, ioqt

from __future__ import annotations
import pickle

import os
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server_old import Context

def human_filesize(size: int) -> str:
    """Return given size in humlan readable format"""
    units = ['B','kB','MB','GB','TB','PB']
    for k in range(len(units)):
        if size < (1024**(k+1)):
            break
    return f"{size/(1024**(k)):4.2f} {units[k]}"

def saveconfig(ctx: Context) -> None:
    """Save the current selected ctf after serialization"""
    logging.debug("Saving config")
    path = ctx.rootpath.joinpath("ctfd", ctx.selected_ctf.name, "config.pkl")
    with open(path, 'wb') as json_file:
        pickle.dump(ctx.selected_ctf, json_file)

    # TODO custom encoder
    ctx.send('[+] Ctfd saved in config.pkl')

def loadconfig(ctx: Context) -> None:
    """Load every saved ctf"""
    logging.debug("Loading config")

    # Enum in all ctfd
    ctf_counter = 0
    for ctf_path in ctx.rootpath.joinpath("ctfd").glob("*"):
        # Last creation date
        lasttime    = 0
        path = ctf_path.joinpath("config.pkl")

        # If file exist
        if path.is_file():
            # Update last file date by default
            timestamp = os.path.getmtime(path)
            if(timestamp > lasttime or lasttime == 0):
                ctf_name = ctf_path.name
                lasttime = timestamp

            # Read config.json
            with open(path, "rb") as file:
                ctf = pickle.load(file)

            ctx.ctf_dict[ctf_name] = ctf
            ctf_counter += 1

            logging.info("%d challenges loaded from : %s", len(ctf.challenge_dict), ctf_name)

    logging.info("%d ctf loaded", ctf_counter)
