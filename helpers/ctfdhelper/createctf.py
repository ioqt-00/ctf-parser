#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec, ioqt

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING
from urllib.parse import urljoin
import argparse
import logging
import subprocess

import requests

from framework.classes import Ctf, Challenge, ChallFile
from utils.other import human_filesize

from . import utils

if TYPE_CHECKING:
    from server import Context

def create_ctf(ctx: Context, args: list) -> None:
    parser = argparse.ArgumentParser(
                description='',
                exit_on_error=False
            )
    parser.add_argument("-t", "--token", help="Analyse all challenges downloaded files")
    parser.add_argument("-u", "--username", help="Analyse all challenges downloaded files")
    parser.add_argument("-p", "--password", help="Analyse all challenges downloaded files")
    parser.add_argument("-n","--ctf_name", help="")
    parser.add_argument("--url", help="")
    parser.add_argument("-f","--flag_format", help="")
    args = parser.parse_args(args)

    password = args.password
    username = args.username
    token = args.token
    url = args.url
    ctf_name = args.ctf_name
    flag_format = args.flag_format

    # Check if Parameters are valid
    if (password is None or username is None) and args.token is None:
        ctx.send("Bad arguments: auth missing")
        ctx.send(parser.format_usage())
        sys.exit()
    elif url is None:
        ctx.send("Bad arguments: url missing")
        ctx.send(parser.format_usage())
        sys.exit()
    elif ctf_name is None:
        ctx.send("Bad arguments: ctf_name missing")
        ctx.send(parser.format_usage())
        sys.exit()

    # Sanitize format flag
    if flag_format is not None:
        ctx.flag_format = flag_format.replace('{','').replace('}','')

    # Creation des setup pour le login
    ctx.request_config['base_url'] = url
    ctx.request_config['username'] = username
    ctx.request_config['password'] = password
    ctx.request_config['token'] = token
    ctx.ctf_name = ctf_name

    login_fetch_parse(ctx)

def update_ctf(ctx: Context, args: list):
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

    # Creation des setup pour le login
    ctx.request_config['base_url'] = ctx.selected_ctf.url
    ctx.request_config['username'] = args.username
    ctx.request_config['password'] = args.password
    ctx.request_config['token'] = args.token
    ctx.ctf_name = ctx.selected_ctf.name

    login_fetch_parse(ctx)

def login_fetch_parse(ctx: Context):
    logging.info("Trying to login to : %s", ctx.request_config['base_url'])
    islogged = utils.login(ctx)
    if not islogged:
        ctx.send("Error during logging")
        sys.exit()
    # Start Parsing
    parse(ctx)

def parse(ctx: Context):
    """Get challenges from ctfd api, parse and create Challenge instances to order them"""
    # Parse infos
    #Parsing challenges
    ctx.send("Getting challenges")
    challenges = utils.get_challenges(ctx)

    challenge_dict = {}
    if ctx.flag_format is None or ctx.flag_format=='':
        ctx.flag_format = 'flag'

    # Enum on All channels
    count = 0
    for challenge in challenges:
        count += 1
        # Info on the challenge
        file_msg = ""
        category, name, description, points, serverside_id, files, solved, link  = challenge
        challenge = Challenge(count, serverside_id, category, name, points, description, solved, link)
        challenge_banner = f"[{category}] {name}"
        challenge_dict[challenge_banner] = challenge

        chall_directory = ctx.rootpath.joinpath("ctfd", ctx.ctf_name, f"{count}_[{category}]_{name}")
        chall_directory.mkdir(parents=True, exist_ok=True)
        challenge.directory = chall_directory
        # IF not already printed
        if(f'[{category}] {name}' not in ctx.challenge_dict.keys()):
            ctx.challenge_dict.update(challenge_dict)

            # Send all file + analyse file if needed
            for challfile in files:
                try:
                    # Check if size is not big
                    url = urljoin(ctx.request_config['base_url'],str(challfile))

                    # Curl file
                    file_resp = requests.get(url, allow_redirects=True)
                    file_name = os.path.basename(file_resp.url).split('?')[0]
                    file_path = chall_directory.joinpath(file_name)
                    # Save file
                    with open(file_path,'wb') as file:
                        file.write(file_resp.content)
                        file_size = file.tell()
                    cmd_list = ["file", file_path]
                    process = subprocess.run(cmd_list, capture_output=True)
                    file_info = str(process.stdout,"utf-8")
                    file_info = file_info.replace(str(file_path),"")[2:]
                    file_size = human_filesize(file_size)
                    file_msg += f"[File]\n**Name**: {file_name}\n**Size**: {file_size}\n**Info**: {file_info}"

                    challfile = ChallFile(file_name, file_path, file_size, file_info)
                    challenge.files.append(challfile)
                except Exception as exception:
                    import traceback
                    res = traceback.format_exception(exception)
                    ctx.send(f"Error in challenge: {name}")
                    ctx.send("".join(res))
                    input()
        else:
            ctx.challenge_dict.update(challenge_dict)

        # Save 
        # If already exist
        saved = False
        for ctf_name, ctf in ctx.ctf_dict.items():
            if ctx.ctf_name==ctf_name:
                saved = True
                for chall_name, chall in challenge_dict.items():
                    ctf.challenge_dict[chall_name] = chall

        # If not created
        if not saved:
            ctf = Ctf(len(ctx.ctf_dict),
                ctx.ctf_name,
                ctx.request_config['base_url'],
                ctx.flag_format,
                challenge_dict
            )
            ctx.ctf_dict[ctf.name] = ctf
            ctx.selected_ctf = ctf

        # Display info
        msg = []
        msg.append(challenge_banner)
        msg.append(f"[Points] {challenge.points}")
        msg.append(f"[Description] {challenge.description}")
        if challenge.link is not None:
            msg.append(f"[Link] {challenge.link}")
        msg.append(file_msg)

        msg = "\n".join(msg)

        msg_file = chall_directory.joinpath("ticket")
        with open(msg_file, "w", encoding="utf-8") as file:
            file.write(msg)
        ctx.send(msg)

        if ctx.DEBUG:
            return

# TODO generic create ctf should be in the FW part, with a function pointing to that function (for instance saveconfig should be shared by all createctf)
