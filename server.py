import argparse
import os
import logging
from urllib.parse import urlparse, urljoin
import requests
from datetime import date
from pathlib import Path

import zmq
import json

from ctfdhelper import utils
from utils.other import human_filesize

challenge_list = {}
all_ctf = []
ctf_name = ""
formatflag = ""
session = requests.Session()
args = {}

CONFIG = {
    'user': None,
    'password': None,
    'base_url': None,
    'token': None,
}

#############################################################################################

def parse_args():
    global args
    parser = argparse.ArgumentParser(description='This tools is used to create automatically discord threads by scraping ctfd plateform and collecting name , category , description and points of challenges.')
    args = parser.parse_args()
    return args

#############################################################################################
session = requests.Session()

def start():
    global challenge_list, all_ctf, ctf_name,formatflag

    # Parse infos
    hostname = urlparse(CONFIG['base_url']).hostname
    
    # Parsing challenges
    CTX.send("Getting challenges")
    challenges = utils.get_challenges(CTX, CONFIG, session)

    current_list = {}
    if(formatflag == None or formatflag == ''):
        formatflag = 'flag'

    # Enum on All channels
    for challenge in challenges:
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
        chall_directory = current_dir.joinpath("ctfd", ctf_name, category, name)
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
                    res_file = os.popen(f'file "{path_file}"').read().split(f"/{name}/{file_name}")[1]
                    file_msg += f"**File**: {file_name}\n**Size**: {human_filesize(size)}\n**Info**: {res_file}"

                    # If size not OK
                    file_msg += f'**Link**: {url}'
                except Exception as e:
                    import traceback
                    res = traceback.format_exception(e)
                    CTX.send(f"Error in challenge: {name}")
                    CTX.send("".join(res))           
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
        CTX.send(msg)

def saveconfig(ctfname=None,flagformat=None):
    global ctf_name,args
    url = ""

    ## Getting actual CTF 
    if (ctfname == None):
        ctfname = ctf_name

    all_ = {}
    ## Check if name is in list
    for i in range(len(all_ctf)):
        if (ctfname in all_ctf[i][1].keys()): 
            ctf_name = all_ctf[i][0]

        if (ctfname in all_ctf[i][0]):
            all_ = all_ctf[i][1]
            url = all_ctf[i][2]
            flagformat = all_ctf[i][3]

    # Starting to create the save object with all info

    # Getting all challenge 
    chall = []
    for element in all_.keys():
        obj = all_[element]
        l = {
            'name': obj[3],
            'points': obj[1],
            'solved': obj[2],
            'flag': obj[4],
            'description': obj[0],
            'thread': obj[5],
            'category': obj[6],
            'id': obj[7],
            'file': obj[8]
        }
        chall.append(l)

    # Final Object
    data = {
        'name': ctfname,
        'url': url,
        'date': str(date.today()),
        'formatflag':flagformat,
        'challenges': chall
    }

    current_dir = Path(__file__).resolve().parent

    # If save option > New file
    path = current_dir.joinpath("ctfd",ctf_name.lower(),"config_0.json")
    
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save the file in Json Format
    with open(path, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, allow_nan=True)

    logging.info('[+] Ctfd saved in config_0.json')

def setup(username, password, token, url):
    CONFIG['base_url'] = url
    CONFIG['username'] = username
    CONFIG['password'] = password
    CONFIG['token'] = token

def createCTF(args_list: list):   # Create CTF
    global ctf_name, challenge_list, formatflag, CONFIG

    parser = argparse.ArgumentParser(description='This tools is used to create automatically discord threads by scraping ctfd plateform and collecting name , category , description and points of challenges.', exit_on_error=False)
    
    parser.add_argument("-t", "--token", help="Analyse all challenges downloaded files")
    parser.add_argument("-u", "--user", help="Analyse all challenges downloaded files")
    parser.add_argument("-p", "--password", help="Analyse all challenges downloaded files")

    parser.add_argument("-n","--ctf_name", help="")
    
    parser.add_argument("--url", help="")

    parser.add_argument("-f","--flag_format", help="")

    args = parser.parse_args(args_list)

    password = args.password
    user = args.user
    token = args.token
    url = args.url

    ctf_name = args.ctf_name
    flag_format = args.flag_format

    # Check if Parameters are valid
    if (args.password is None or args.user is None) and args.token is None:
        CTX.send("Bad arguments: auth missing")
        raise argparse.ArgumentError
    elif args.url is None:
        CTX.send("Bad arguments: url missing")
        raise argparse.ArgumentError
    elif args.ctf_name is None:
        CTX.send("Bad arguments: ctf_name missing")
        raise argparse.ArgumentError

    # Sanitize format flag
    if(flag_format != None):
        formatflag = flag_format.replace('{','').replace('}','')

    # Creation des setup pour le login
    setup(user, password, token, url)

    # Login to CTFD
    logging.info(f"Trying to login to : {url}")  
    islogged, CONFIG = utils.login(CTX, CONFIG, session)

    if not islogged:
        CTX.send("Error during logging")
        exit()

    # Start Parsing
    start()  # Start

    # Save in config.json
    saveconfig(ctf_name)

    logging.info("Thread Creation END")

##########################################################################################################################

class Context():
    def send(self, msg):
        SOCKET.send_string(msg)

    def recv(self):
        return SOCKET.recv_string()

def not_implemented():
    CTX.send("Not implemented")

def main_switch(cmd, args):
    if cmd == "createCTF":
        createCTF(args)
    elif cmd == "flagged":
        not_implemented()
    elif cmd == "end":
        not_implemented()
    elif cmd == "format":
        not_implemented()
    else:
        CTX.send(f"Command not found: {cmd}")
    CTX.send(f"EOL")

if __name__ == '__main__':
    args = parse_args()
    if not os.path.isdir('ctfd'):
        os.makedirs('ctfd', exist_ok=True) 
    
    context = zmq.Context()
    SOCKET = context.socket(zmq.PAIR)
    SOCKET.bind('tcp://127.0.0.1:5555')
    CTX = Context()
    while True:
        try:
            msg = CTX.recv()
            if msg != "":
                cmd_args = msg.split()
                cmd = cmd_args[0].strip()
                args = cmd_args[1:]
                res = main_switch(cmd, args)
        except Exception as e:
            import traceback
            res = traceback.format_exception(e)
            CTX.send("".join(res))       
            CTX.send("EOL")     
        except SystemExit:
            CTX.send("EOL")