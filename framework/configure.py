#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: ioqt

from __future__ import annotations

import sys
import argparse
from typing import TYPE_CHECKING

from framework import not_implemented
from helpers import ctfdhelper, rctf_helper
if TYPE_CHECKING:
    from server import Context


def configure():
    not_implemented()

def auth(ctx: Context, args: list):
    parser = argparse.ArgumentParser(
            description='',
            exit_on_error=False
        )
    parser.add_argument("-t", "--token", help="Analyse all challenges downloaded files")
    parser.add_argument("-u", "--username", help="Analyse all challenges downloaded files")
    parser.add_argument("-p", "--password", help="Analyse all challenges downloaded files")
    args = parser.parse_args(args)

    # Check if Parameters are valid
    if (args.password is None or args.username is None) and args.token is None:
        ctx.send("Bad arguments: auth missing")
        ctx.send(parser.format_usage())
        sys.exit() 
    if ctx.selected_ctf is None:
        ctx.send("Select a ctf first")
        sys.exit()

    if args.username is not None:
        ctx.request_config['username'] = args.username
    if args.password is not None:
        ctx.request_config['password'] = args.password
    if args.token is not None:
        ctx.request_config['token'] = args.token
    ctx.request_config['base_url'] = ctx.selected_ctf.url

    if ctx.endpoint == "ctfd":
        ctfdhelper.utils.login(ctx)
    elif ctx.endpoint == "rctf":
        rctf_helper.utils.login(ctx)
    else:
        not_implemented()
