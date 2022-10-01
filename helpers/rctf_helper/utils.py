#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec, ioqt

from __future__ import annotations

from urllib.parse import urljoin
from typing import TYPE_CHECKING, Union, List, Dict
import logging
import json
import re

import requests

from framework.utils import UrlPath
if TYPE_CHECKING:
    from server import Context

def fetch(ctx: Context, url: str, request_session: requests.Session) -> Union[List[dict], dict]:
    res = request_session.get(url)
    data = res.json()
    if not res.ok or data["kind"]!="goodChallenges":
        msg = "Failed fetching challenge!"
        logging.error(res.text)
        ctx.send(msg)
        return None
    return res.json()['data']

def login(ctx: Context) -> bool:
    """Helper to log into ctfd server using either username/password credentials
    or api token"""
    config = ctx.request_config
    session = ctx.request_session
    if config['token'] is not None:
        ctx.send('**[+] Login using token ...**')
        session.headers.update({"Content-Type": "application/json"})
        session.headers.update({"Authorization": f"Bearer {config['token']}"})
        resp = session.get(config['base_url']+'/api/v1/users/me').text

        # Valid token ?
        if 'success\": true' in resp or "goodUserData" in resp:
            config['username'] = json.loads(resp)["data"]["name"]
            return True
        else:
            msg = json.loads(resp)["message"]
            ctx.send(f"```\nMessage:\n{msg}```")
    # login with user and password
    else:
        # Get in main page
        resp = requests.get(config['base_url']).text

        # If recaptcha Detected > Trigger
        if('https://www.google.com/recaptcha/api.js' in resp):
            # If token stored > Login
            # Help message > store the token
            logging.info('Recaptcha Detected !!')
            ctx.send('**[+] Recaptcha Detected !!**')
            prefix = config['PREFIX']
            ctx.send(f'** ->  use: {prefix}token "your token"**')
            return False
        else:
            # If normal CTFD
            nonce = get_nonce(config,session)

            # Login
            res = session.post(
                urljoin(config['base_url'], '/login'),
                data={
                    'name': config['username'],
                    'password': config['password'],
                    'nonce': nonce,
                }
            )

            # Keycheck
            if 'incorrect' in res.text:
                logging.error('Unable to Login With those credentials')
                return False
            elif 'success\": true' in session.get(config['base_url']+'/api/v1/users/me').text:
                return True

    return False

def get_nonce(config: Dict, request_session: requests.Session) -> str:
    """Regex to get 'nonce token' in html page"""
    res = request_session.get(urljoin(config['base_url'], '/login'))
    match = re.search('name="nonce"(?:[^<>]+)?value="([0-9a-f]{64})"', res.text)
    if match is not None:
        return match.group(1)
    return ""

def get_challenges(ctx: Context):
    """Get challenges via ctfd flag flag{omg_its_rsa}api and order them in a list"""
    logging.info('Getting challenges ...')

    config = ctx.request_config
    request_session = ctx.request_session

    # Get All challenges
    challenges = fetch(ctx,urljoin(config['base_url'], '/api/v1/challs'), request_session)
    result = []

    # Get info challenge one per one
    for challenge in challenges:
        try:
            # Get Files
            files = []
            if('files' in challenge):
                files = challenge['files']

            #Other Infos  
            category = challenge['category']
            name = challenge['name'].replace(' ','_')  
            description = str(challenge['description'])
            points = str(challenge['points'])
            solved = False
            link = None
            
            # Add all info in 'result' list
            result.append([category, name, description, points, challenge["id"], files, solved, link])
        except Exception as ex:
            logging.error("Error during fetching/grabbing a challenge")
            logging.error(ex)
            ctx.send(ex)

        if ctx.DEBUG:
            break

    return sorted(result)

def flag(ctx: Context, flag: str):
    url = UrlPath(ctx.selected_ctf.url)
    url = url.joinpath("api/v1/challs/", ctx.selected_challenge.serverside_id, "submit")
    data = {"flag":flag}
    res = ctx.request_session.post(url, json=data)
    if not res.ok:
        ctx.send(res.json())
        exit()
    return res.json()['data']

def get_solved_challenges(ctx: Context):
    url = UrlPath(ctx.selected_ctf.url)
    url = url.joinpath("api/v1/users/me")
    res = ctx.request_session.get(url)
    data = res.json()["data"]
    return data["solves"]
