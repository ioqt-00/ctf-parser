#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

from __future__ import annotations
from dataclasses import dataclass, asdict
import pickle

import random
import os
import subprocess
import glob
import operator
from time import sleep
import logging
from datetime import date
from typing import Dict, TYPE_CHECKING
import json
from unicodedata import category

if TYPE_CHECKING:
    from framework.classes import Ctf, Challenge

def cleanpath(path):
    return os.path.relpath(os.path.normpath(os.path.join("/", path)), "/")

def findfile(name):
    found = []
    for file in glob.glob("./**/%s"%cleanpath(name), recursive = True):
        found.append(file)
    return found

def finddirectory(name):
    found = []
    for file in glob.glob("./**/%s"%(cleanpath(name)), recursive = True):
        found.append(file)
    return found


def rdnname():
	return str(random.randint(11111111,99999999))

def writefile(path,data):
	f = open(path, "a")
	f.write(data)
	f.close()
	
def readfile(path):
	f = open(path, "rb")
	cnt = f.read()
	f.close()
	return cnt

## Append Result to result list
def append_result(result,command,cnt):
    if(os.path.isfile(cnt)):
        if(cnt.endswith('.txt') and sizeok(cnt,3.00,operator.lt)):

            # Clean for StegSeek Seed    
            data = '\n'.join(x for x in open(cnt,'r').read().split('\n') if '[i] Progress' not in x)
            
            if(len(data) < 2000):
                result.append('**%s**```\n%s\n```'%(command,data))
            else:
                result.append(['**%s**'%command,cnt])
        else:
            result.append(['**%s**'%command,cnt])
    else:
        if len(cnt) < 2000  and 'strings' != command.lower():
            result.append('**%s**```\n%s\n```'%(command,cnt))
        else:
            rdn_name = rdnname()
            writefile('/tmp/%s.txt'%str(rdn_name),cnt)
            result.append(['**%s**'%command,'/tmp/%s.txt'%str(rdn_name)])
    return result

def sizeok(filename,max_=7.50,symbol = operator.lt):
    # Check if Size is ok for Discord 

    if os.path.isfile(filename):
        size = os.path.getsize(filename)
        if symbol(int(size)//(1024*1024),max_):
            return True
        else:
            return False
    else:
        return False

def human_filesize(l):

    # Convert file Lenght   
    units = ['B','kB','MB','GB','TB','PB']
    for k in range(len(units)):
        if l < (1024**(k+1)):
            break

    return "%4.2f %s" % (round(l/(1024**(k)),2), units[k])

def download(filename,path):
    try:
        # Try to curl > Save in file
        subprocess.run(["curl %s -o %s"%(filename,path)],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        if(os.path.isfile(path)):
            return True
        else:
            return False
    except Exception as ex:
        logger(ex,'error',1,1)
        return False

# def execmd(cmd):
#     return subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()[0].decode()

def execmd(cmd,t=0.5):
    cnt = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    for k in range(int(t*60)):
        sleep(1)
        if(cnt.poll() is not None):
            try:
                return tuple(x for x in cnt.communicate() if x!=b'')[0].decode()
            except Exception as ex:
                print(ex)
                return None
    cnt.kill()
    return None

def saveconfig(ctx, ctf_dict: Dict[str, Ctf], ctf_name: str, flag_format: str):
    # Save the current selected ctf after serialization
    path = ctx.rootpath.joinpath("ctfd", ctf_name, "config.pkl")
    with open(path, 'wb') as json_file:
        pickle.dump(ctx.selected_ctf, json_file)

    # TODO custom encoder
    ctx.send('[+] Ctfd saved in config.pkl')

def loadconfig(ctx):
    # Last creation date
    lasttime    = 0

    # Enum in all ctfd
    ctf_counter = 0
    for ctf_path in ctx.rootpath.joinpath("ctfd").glob("*"):
        ctf_counter += 1
        path = ctf_path.joinpath("config.pkl")

        # If file exist
        if path.is_file():
            # Update last file date by default
            t = os.path.getmtime(path)
            if(t > lasttime or lasttime == 0):
                ctf_name = ctf_path.name
                lasttime = t

            # Read config.json
            with open(path, "rb") as file:
                ctf = pickle.load(file)

            ctx.ctf_dict["ctf_name"] = ctf

            logging.info("%d challenges loaded from : %s", len(ctf.challenge_dict), ctf_name)

    logging.info("All Challenges loaded !")
