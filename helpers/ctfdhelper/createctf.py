from urllib.parse import urlparse, urljoin
import argparse
import logging 
from pathlib import Path
import subprocess
import requests
import os

from . import utils
from utils.other import human_filesize

def create_ctf(ctx, args_list, CONFIG):
    parser = argparse.ArgumentParser(description='This tools is used to create automatically discord threads by scraping ctfd plateform and collecting name , category , description and points of challenges.', exit_on_error=False)
    
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
        raise argparse.ArgumentError
    elif url is None:
        ctx.send("Bad arguments: url missing")
        raise argparse.ArgumentError
    elif ctf_name is None:
        ctx.send("Bad arguments: ctf_name missing")
        raise argparse.ArgumentError

    # Sanitize format flag
    if(flag_format != None):
        formatflag = flag_format.replace('{','').replace('}','')

    # Creation des setup pour le login
    CONFIG['base_url'] = url
    CONFIG['username'] = username
    CONFIG['password'] = password
    CONFIG['token'] = token

    # Login to CTFD
    logging.info(f"Trying to login to : {url}")  
    islogged, CONFIG = utils.login(ctx, CONFIG, ctx.session)

    if not islogged:
        ctx.send("Error during logging")
        exit()

    # Start Parsing
    parse(ctx, CONFIG)  # Start

    logging.info("Thread Creation END")

    return CONFIG

def parse(ctx, CONFIG):
    # Parse infos
    hostname = urlparse(CONFIG['base_url']).hostname
    
    #Parsing challenges
    ctx.send("Getting challenges")
    challenges = utils.get_challenges(ctx, CONFIG, ctx.session)

    current_list = {}
    if(formatflag == None or formatflag == ''):
        formatflag = 'flag'

    # Enum on All channels
    count = 0
    for challenge in challenges:
        count += 1
        # Info on the challenge
        msg = ""
        file_msg = ""
        category, name, description, points, id_, files  = challenge
        current_list[f'[{category}] {name}'] = [
                                                description, 
                                                points, 
                                                False, 
                                                name, 
                                                "",
                                                0,
                                                category,
                                                id_,
                                                files
                                            ]

        current_dir = Path(__file__).resolve().parent
        chall_directory = current_dir.joinpath("ctfd", ctf_name, f"[{count}] [{category}] {name}")
        chall_directory.mkdir(parents=True, exist_ok=True)
        # IF not already printed 
        if(f'[{category}] {name}' not in challenge_list.keys()):
            challenge_list.update(current_list)

            # Send all file + analyse file if needed
            for chall in files:
                try:
                    # Check if size is not big
                    url = urljoin(CONFIG['base_url'],str(chall))

                    # Curl file
                    file_resp = requests.get(url, allow_redirects=True)
                    file_name = os.path.basename(file_resp.url).split('?')[0]
                    path_file = chall_directory.joinpath(file_name)
                    # Save file
                    with open(path_file,'wb') as f:
                        f.write(file_resp.content)
                        size = f.tell()
                    cmd_list = ["file", path_file]
                    res_file = ""
                    process = subprocess.run(cmd_list, capture_output=True)
                    res_file = str(process.stdout,"utf-8")
                    file_msg += f"**File**: {file_name}\n**Size**: {human_filesize(size)}\n**Info**: {res_file}"
                except Exception as e:
                    import traceback
                    res = traceback.format_exception(e)
                    ctx.send(f"Error in challenge: {name}")
                    ctx.send("".join(res))           
        else:
            challenge_list.update(current_list)

        # Save 
        # If already exist
        saved = False
        for ctf in all_ctf:
            if(ctf_name == ctf[0]):
                saved = True
                for chall in current_list.keys():
                    if(chall not in ctf[1].keys()):
                        ctf[1][str(current_list[chall])] = current_list[chall]

        # If not created
        if(saved == False):
            all_ctf.append([ctf_name, current_list, CONFIG['base_url'],formatflag])

        # Display info
        msg += (f'[{category}] {name}\n')
        msg += (f"[Points] {points}\n")
        msg += (f"[Description] " + str(challenge_list[f'[{category}] {name}'][0])+ "\n\n")
        msg += file_msg
        msg += "\n"

        msg_file = chall_directory.joinpath("ticket")
        with open(msg_file, "w") as f:
            f.write(msg)
        ctx.send(msg)
