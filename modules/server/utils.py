from monitorizer.ui.arguments import args as argsc
import requests
import os

def reload_watchlist():
    if not os.path.isfile(argsc.watch):
        return []
    return [t.strip() for t in open(argsc.watch,"r").readlines() if t.strip()]

def rewrite_watchlist(watchlist):
    if not os.path.isfile(argsc.watch):
        return []
    open(argsc.watch , 'w').write('\n'.join(watchlist))

def is_alive(url):
    try:
        requests.head(f'https://{url}', timeout=25)
        return 1
    except:
        try:
            requests.head(f'http://{url}', timeout=25)
            return 1
        except:
            return 0
        return 0