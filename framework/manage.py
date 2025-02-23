#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: ioqt

from __future__ import annotations
import argparse
import logging
from typing import TYPE_CHECKING
import sys

from prettytable import PrettyTable

from helpers import ctfdhelper, rctf_helper
from utils.other import saveconfig
from framework.utils import not_implemented
if TYPE_CHECKING:
    from server import Context

def list_(ctx: Context, args_list: list):
    logging.debug("Listing ctf or challenges")
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--ctf", action='store_true', help="List ctf")
    parser.add_argument("--challenge", action='store_true', help="List challenges in selected ctf")
    args = parser.parse_args(args_list)

    ctf = args.ctf
    challenge = args.challenge

    if not challenge and not ctf:
        if ctx.selected_ctf is None:
            ctf=True
        else:
            challenge=True
    if challenge and ctx.selected_ctf is None:
        ctx.send("Bad arguments: please select a ctf first")
        sys.exit()
    if challenge:
        list_challenges(ctx)
    elif ctf:
        list_ctf(ctx)

def list_challenges(ctx: Context):
    logging.debug("Listing challenges")

    table = PrettyTable(["Id", "Category", "Name", "Points", "Flagged"])
    for challenge in ctx.selected_ctf.challenge_dict.values():
        if challenge.solved:
            flagged = "[X]"
        else:
            flagged = "[ ]"
        table.add_row([challenge.id, challenge.category, challenge.name, challenge.points, flagged])
    ctx.send(str(table))

def list_ctf(ctx: Context):
    logging.debug("Listing ctf")
    for ctf in ctx.ctf_dict.values():
        msg = f"[{ctf.id}] {ctf.name} : {len(ctf.challenge_dict.keys())} challenges."
        ctx.send(msg)

def select(ctx: Context, args_list: list):
    logging.debug("Selecting ctf or challenge")
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('id', type=int, help='Id of either chall or ctf to select')
    parser.add_argument("--ctf-id", action='store_true', help="Select ctf")
    parser.add_argument("--challenge-id",
                        action='store_true',
                        help="Select challenge in selected ctf"
                    )
    args = parser.parse_args(args_list)

    ctf_id = args.ctf_id
    challenge_id = args.challenge_id
    id = args.id

    if not challenge_id and not ctf_id:
        if ctx.selected_ctf is None:
            ctf_id = True
        else:
            challenge_id = True
    if challenge_id and ctx.selected_ctf is None:
        ctx.send("Bad arguments: please select a ctf first")
        sys.exit()
    if challenge_id:
        select_challenge(ctx, id)
    elif ctf_id:
        select_ctf(ctx, id)

def select_challenge(ctx: Context, challenge_id: int) -> None:
    logging.debug("Selecting challenge")
    for challenge in ctx.selected_ctf.challenge_dict.values():
        if challenge.id == challenge_id:
            ctx.selected_challenge = challenge
            return
    ctx.send("Challenge id not found in challenge list")
    sys.exit()

def select_ctf(ctx: Context, ctf_id: int):
    logging.debug("Selecting ctf")
    for ctf in ctx.ctf_dict.values():
        if ctf.id == ctf_id:
            ctx.selected_ctf = ctf
            ctx.ctf_name = ctf.name
            return
    ctx.send("CTF id not found in CTF list")
    sys.exit()

def flag(ctx: Context, args_list: list):
    logging.debug("Flagging challenge")
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('flag', nargs='?', type=str, help='')
    args = parser.parse_args(args_list)
    if ctx.selected_challenge is None:
        ctx.send("You must select a challenge first")
        sys.exit()
    if args.flag is not None:
        ctx.selected_challenge.flag = args.flag

        if ctx.endpoint == "rctf":
            rctf_helper.flag(ctx, args.flag)
        else:
            not_implemented()
    ctx.selected_challenge.solved = True
    saveconfig(ctx)

def create_ctf(ctx: Context, args: list):
    logging.info("Launching appropriate create_ctf")
    if ctx.endpoint == "ctfd":
        ctfdhelper.create_ctf(ctx, args)
    elif ctx.endpoint == "rctf":
        rctf_helper.create_ctf(ctx, args)
    else:
        not_implemented()
    saveconfig(ctx)

def update(ctx: Context, args: list):
    logging.info("Updating selected ctf")
    if ctx.selected_ctf is None:
        ctx.send("Bad arguments: please select a ctf first")
        sys.exit()

    if ctx.endpoint == "ctfd":
        ctfdhelper.update_ctf(ctx, args)
    elif ctx.endpoint == "rctf":
        rctf_helper.update_ctf(ctx, args)
    else:
        not_implemented()
    saveconfig(ctx)


def show(ctx: Context, args_list: list):
    logging.debug("Showing challenge")
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('id', nargs="?", type=int, help='Id of chall to show')
    args = parser.parse_args(args_list)

    if args.id is None and ctx.selected_challenge is None:
        ctx.send("You must select a challenge first")
        sys.exit()
    if args.id is not None:
        if ctx.selected_ctf is None:
            ctx.send("You must select a ctf first")
            sys.exit()
        select_challenge(ctx, args.id)

    data = ctx.selected_challenge.json()
    ctx.send(data)
