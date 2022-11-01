import argparse
import json
import requests

from framework.utils import not_implemented

#############################################################################################

def create_ctf(args):
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

    res = requests.get(SERVER + "create-ctf", json=json.dumps(vars(args)))
    print(res.text)

def list_(args):
    parser = argparse.ArgumentParser(
                description='',
                exit_on_error=False
            )
    parser.add_argument("--ctf", action='store_true', help="List ctf")
    parser.add_argument("--challenge", action='store_true', help="List challenges in selected ctf")
    args = parser.parse_args(args)

    res = requests.get(SERVER + "list", json=json.dumps(vars(args)))
    
    res = res.json()

    print(res.get("msg"))

def select(args):
    parser = argparse.ArgumentParser(
                description='',
                exit_on_error=False
            )
    parser.add_argument('id', type=int, help='Id of either chall or ctf to select')
    parser.add_argument("--ctf-id", action='store_true', help="Select ctf")
    parser.add_argument("--challenge-id",
                        action='store_true',
                        help="Select challenge in selected ctf"
                    )
    args = parser.parse_args(args)

    res = requests.get(SERVER + "select", json=json.dumps(vars(args)))
    print(res.json().get("msg"))

def configure():
    res = requests.get(SERVER + "configure")
    print(res.json().get("msg"))

def flag(args):
    parser = argparse.ArgumentParser(
            description='',
            exit_on_error=False
        )
    parser.add_argument('flag', nargs='?', type=str, help='')
    args = parser.parse_args(args)
    res = requests.get(SERVER + "flag", json=json.dumps(vars(args)))
    print(res.json().get("msg"))

def show(args):
    parser = argparse.ArgumentParser(
        description='',
        exit_on_error=False
    )
    parser.add_argument('id', nargs="?", type=int, help='Id of chall to show')
    args = parser.parse_args(args)
    res = requests.get(SERVER + "show", json=json.dumps(vars(args)))
    print(res.text)
    print(res.json().get("msg"))

def auth(args):
    parser = argparse.ArgumentParser(
            description='',
            exit_on_error=False
        )
    parser.add_argument("-t", "--token", help="Analyse all challenges downloaded files")
    parser.add_argument("-u", "--username", help="Analyse all challenges downloaded files")
    parser.add_argument("-p", "--password", help="Analyse all challenges downloaded files")
    args = parser.parse_args(args)
    res = requests.get(SERVER + "auth", json=json.dumps(vars(args)))
    print(res.json().get("msg"))

def update(args):
    parser = argparse.ArgumentParser(
            description='',
            exit_on_error=False
        )
    parser.add_argument("-t", "--token", help="Analyse all challenges downloaded files")
    parser.add_argument("-u", "--username", help="Analyse all challenges downloaded files")
    parser.add_argument("-p", "--password", help="Analyse all challenges downloaded files")
    args = parser.parse_args(args)
    res = requests.get(SERVER + "update", json=json.dumps(vars(args)))
    print(res.json().get("msg"))

def reset():
    res = requests.get(SERVER + "reset")
    print(res.json().get("msg"))

def main_switch(cmd, args) -> None:
    if cmd == "createCTF":
        create_ctf(args)
    elif cmd in set(["list","ls"]):
        list_(args)
    elif cmd in set(["select","cd"]):
        select(args)
    elif cmd == "config":
        configure()
    elif cmd == "flag":
        flag(args)
    elif cmd == "show":
        show(args)
    elif cmd == "reset":
        reset()
    elif cmd == "auth":
        auth(args)
    elif cmd == "update":
        update(args)
    else:
        print(f"Command not found: {cmd}")
    
if __name__ == '__main__':
    SERVER = "http://127.0.0.1:5000/"

    while True:
        print("> ", end="")
        cmd = input("")
        args = cmd.split()
        cmd = args[0].strip()
        args = args[1:]
        main_switch(cmd, args)
