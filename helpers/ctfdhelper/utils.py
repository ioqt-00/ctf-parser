from urllib.parse import urljoin
from typing import Union, List
import logging
import json
import requests

def fetch(ctx, url: str, request_session) -> Union[List[dict], dict]:
    res = request_session.get(url)
    if '{\"message' in res.text:
        msg = res.json()['message']
        ctx.send(f'** [+] {msg}**')
    elif not res.ok or not res.json()['success']:
        logging.error('Failed fetching challenge!')
        exit(1)
    else:
        return res.json()['data']

def login(ctx, CONFIG, request_session):
    if CONFIG['token'] != None:
        ctx.send('**[+] Login using token ...**')
        request_session.headers.update({"Content-Type": "application/json"})
        request_session.headers.update({"Authorization": f"Token {CONFIG['token']}"})
        resp = request_session.get(CONFIG['base_url']+'/api/v1/users/me').text

        # Valid token ? 
        if('success\": true' in resp):
            CONFIG['username'] = json.loads(resp)["data"]["name"]
            return True,CONFIG
        else:
            msg = json.loads(resp)["message"]
            ctx.send(f"```\nMessage:\n{msg}```")
            return False,CONFIG
    # login with user and password
    else:      
        # Get in main page
        resp = requests.get(CONFIG['base_url']).text
        
        # If recaptcha Detected > Trigger 
        if('https://www.google.com/recaptcha/api.js' in resp):
            # If token stored > Login
            # Help message > store the token
            logging.info('Recaptcha Detected !!')
            ctx.send('**[+] Recaptcha Detected !!**')
            prefix = CONFIG['PREFIX']
            ctx.send(f'** ->  use: {prefix}token "your token"**')
            return False,CONFIG
        else:
            # If normal CTFD
            nonce = get_nonce(CONFIG,request_session)

            # Login
            res = request_session.post(
                urljoin(CONFIG['base_url'], '/login'),
                data={
                    'name': CONFIG['username'],
                    'password': CONFIG['password'],
                    'nonce': nonce,
                }
            )

            # Keycheck
            if 'incorrect' in res.text:
                logging.error('Unable to Login With those credentials')
                return False,CONFIG
            elif 'success\": true' in request_session.get(CONFIG['base_url']+'/api/v1/users/me').text:
                return True,CONFIG
            else:
                return False,CONFIG

    return False,CONFIG

def get_challenges(ctx, CONFIG, request_session):
    logging.info('Getting challenges ...')

    # Get All challenges
    challenges = fetch(ctx,urljoin(CONFIG['base_url'], '/api/v1/challenges'), request_session)
    result = []

    # Get info challenge one per one
    for challenge in challenges:
        try:
            # Fetch api
            res = fetch(ctx,urljoin(CONFIG['base_url'], '/api/v1/challenges/%s'%challenge["id"]), request_session)
            
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
            logging("Error during fetching/grabbing a challenge")
            pass

    return sorted(result)
