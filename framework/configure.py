#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: ioqt

from __future__ import annotations

from typing import TYPE_CHECKING

from framework import not_implemented
from helpers import ctfdhelper, rctf_helper
if TYPE_CHECKING:
    from server import Context


def configure():
    not_implemented()

def auth(ctx: Context, args: dict):
    username = args.get("username")
    password = args.get("password")
    token = args.get("token")

    # Check if Parameters are valid
    if (password is None or username is None) and token is None:
        ctx.send("Bad arguments: auth missing")
        return False
    if ctx.selected_ctf is None:
        ctx.send("Select a ctf first")
        return False

    if username is not None:
        ctx.request_config['username'] = username
    if password is not None:
        ctx.request_config['password'] = password
    if token is not None:
        ctx.request_config['token'] = token
    ctx.request_config['base_url'] = ctx.selected_ctf.url

    if ctx.endpoint == "ctfd":
        ctfdhelper.utils.login(ctx)
    elif ctx.endpoint == "rctf":
        rctf_helper.utils.login(ctx)
    else:
        not_implemented()
