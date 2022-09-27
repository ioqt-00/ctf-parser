#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

def download(filename,path):
    try:
        # Try to curl > Save in file
        subprocess.run(["curl %s -o %s"%(filename,path)],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        if(os.path.isfile(path)):
            return True
        else:
            return False
    except Exception as exc:
        logging.error(exc)
        return False

# def execmd(cmd):
#     return subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()[0].decode()

def execmd(cmd,t=0.5):
    cnt = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    for _ in range(int(t*60)):
        sleep(1)
        if(cnt.poll() is not None):
            try:
                return tuple(x for x in cnt.communicate() if x!=b'')[0].decode()
            except Exception as ex:
                print(ex)
                return None
    cnt.kill()
    return None

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

## Append Result to result list
def append_result(result,command,cnt):
    if os.path.isfile(cnt):
        if(cnt.endswith('.txt') and sizeok(cnt,3.00,operator.lt)):

            # Clean for StegSeek Seed
            data = '\n'.join(x for x in open(cnt,'r').read().split('\n') if '[i] Progress' not in x)

            if len(data) < 2000:
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
    return False