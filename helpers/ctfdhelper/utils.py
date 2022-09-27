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

if TYPE_CHECKING:
    from server import Context

def fetch(ctx: Context, url: str, request_session: requests.Session) -> Union[List[dict], dict]:
    res = request_session.get(url)
    if '{\"message' in res.text:
        msg = res.json()['message']
        ctx.send(f'** [+] {msg}**')
        return None
    if not res.ok or not res.json()['success']:
        msg = "Failed fetching challenge!"
        logging.error(msg)
        ctx.send(msg)
        return None
    return res.json()['data']

def login(ctx: Context) -> bool:
    """Helper to log into ctfd server using either username/password credentials
    or api token"""
    config = ctx.config
    session = ctx.request_session
    if config['token'] is not None:
        ctx.send('**[+] Login using token ...**')
        session.headers.update({"Content-Type": "application/json"})
        session.headers.update({"Authorization": f"Token {config['token']}"})
        resp = session.get(config['base_url']+'/api/v1/users/me').text

        # Valid token ?
        if 'success\": true' in resp:
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
    """Get challenges via ctfd api and order them in a list"""
    logging.info('Getting challenges ...')

    config = ctx.config
    request_session = ctx.request_session

    # Get All challenges
    challenges = fetch(ctx,urljoin(config['base_url'], '/api/v1/challenges'), request_session)
    result = []

    # Get info challenge one per one
    for challenge in challenges:
        try:
            # Fetch api
            res = fetch(ctx,urljoin(config['base_url'], f"/api/v1/challenges/{challenge['id']}"), request_session)
            
            # Get Files
            file = []
            if('files' in res):
                file = res['files']

            #Other Infos  
            category = res['category']
            name = res['name'].replace(' ','_')  
            description = str(res['description']).replace('\r', '').replace('\n', '')
            points = str(res['value'])
            
            # Add all info in 'result' list
            result.append([category, name, description, points,challenge["id"],file])
        except Exception as ex:
            logging.error("Error during fetching/grabbing a challenge")
            logging.error(ex)
            ctx.send(ex)

    return sorted(result)
