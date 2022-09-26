import os
import sys
from urllib.parse import urlparse, urljoin
import argparse
import logging
from pathlib import Path
import subprocess

import requests

from . import utils
from framework.classes import Ctf, Challenge
from utils.other import human_filesize

def create_ctf(ctx, args_list) -> None:
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
    args = parser.parse_args(args_list)

    password = args.password
    username = args.username
    token = args.token
    url = args.url
    ctf_name = args.ctf_name
    flag_format = args.flag_format

    # Check if Parameters are valid
    if (password is None or username is None) and args.token is None:
        ctx.send("Bad arguments: auth missing")
        sys.exit()
    elif url is None:
        ctx.send("Bad arguments: url missing")
        sys.exit()
    elif ctf_name is None:
        ctx.send("Bad arguments: ctf_name missing")
        sys.exit()

    # Sanitize format flag
    if flag_format is not None:
        ctx.flag_format = flag_format.replace('{','').replace('}','')

    # Creation des setup pour le login
    ctx.CONFIG['base_url'] = url
    ctx.CONFIG['username'] = username
    ctx.CONFIG['password'] = password
    ctx.CONFIG['token'] = token
    ctx.ctf_name = ctf_name

    # Login to CTFD
    logging.info("Trying to login to : %s", url)
    islogged, ctx.CONFIG = utils.login(ctx, ctx.CONFIG, ctx.request_session)

    if not islogged:
        ctx.send("Error during logging")
        sys.exit()

    # Start Parsing
    parse(ctx)  # Start
    logging.info("Thread Creation END")

def parse(ctx):
    # Parse infos
    #Parsing challenges
    ctx.send("Getting challenges")
    challenges = utils.get_challenges(ctx, ctx.CONFIG, ctx.request_session)

    challenge_dict = {}
    if ctx.flag_format is None or ctx.flag_format=='':
        ctx.flag_format = 'flag'

    # Enum on All channels
    count = 0
    for challenge in challenges:
        count += 1
        # Info on the challenge
        file_msg = ""
        category, name, description, points, id_, files  = challenge
        challenge = Challenge(id_, category, name, points, description, files)
        challenge_banner = f"[{category}] {name}"
        challenge_dict[challenge_banner] = challenge

        chall_directory = ctx.rootpath.joinpath("ctfd", ctx.ctf_name, f"[{count}] [{category}] {name}")
        chall_directory.mkdir(parents=True, exist_ok=True)
        challenge.directory = chall_directory
        # IF not already printed
        if(f'[{category}] {name}' not in ctx.challenge_dict.keys()):
            ctx.challenge_dict.update(challenge_dict)

            # Send all file + analyse file if needed
            for chall in files:
                try:
                    # Check if size is not big
                    url = urljoin(ctx.CONFIG['base_url'],str(chall))

                    # Curl file
                    file_resp = requests.get(url, allow_redirects=True)
                    file_name = os.path.basename(file_resp.url).split('?')[0]
                    path_file = chall_directory.joinpath(file_name)
                    # Save file
                    with open(path_file,'wb') as f:
                        f.write(file_resp.content)
                        size = f.tell()
                    challenge.files.append(path_file)
                    cmd_list = ["file", path_file]
                    res_file = ""
                    process = subprocess.run(cmd_list, capture_output=True)
                    res_file = str(process.stdout,"utf-8")
                    res_file = res_file.replace(path_file,"")[2:]
                    file_msg += f"[File]\n**Name**: {file_name}\n**Size**: {human_filesize(size)}\n**Info**: {res_file}"
                except Exception as exception:
                    import traceback
                    res = traceback.format_exception(exception)
                    ctx.send(f"Error in challenge: {name}")
                    ctx.send("".join(res))
        else:
            ctx.challenge_dict.update(challenge_dict)

        # Save 
        # If already exist
        saved = False
        for ctf_name,ctf in ctx.ctf_dict.items():
            if ctx.ctf_name==ctf_name:
                saved = True
                for chall_name, chall in challenge_dict.items():
                    if chall_name not in ctf.challenge_dict.keys():
                        ctf.challenge_dict[chall_name] = chall

        # If not created
        if not saved:
            ctf = Ctf(0,
                ctx.ctf_name,
                ctx.CONFIG['base_url'],
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
        msg.append(file_msg)

        msg = "\n".join(msg)

        msg_file = chall_directory.joinpath("ticket")
        with open(msg_file, "w", encoding="utf-8") as file:
            file.write(msg)
        ctx.send(msg)

# TODO generic create ctf should be in the FW part, with a function pointing to that function (for instance saveconfig should be shared by all createctf)