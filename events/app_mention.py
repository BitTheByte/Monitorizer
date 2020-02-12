from flask import Flask
from flask import request
import types
import templates
import requests
import re
import sys,os
import logging
import threading
import monitorizer

app        = Flask("HELLO")
watchlist  = [t.strip() for t in open(monitorizer.args.watch,"r").readlines()]
seen       = []

def is_alive(url):
    try:
        requests.head('https://' + url)
        return 1
    except:
        try:
            requests.head('http://'  + url)
            return 1
        except:
            return 0
        return 0

def _help(args):
    metadata_github = monitorizer.metadata_github()
    metedata_local  = monitorizer.metadata

    if metedata_local["version"]["monitorizer"] < metadata_github["version"]["monitorizer"]:
        code_base_update = 1
    else:
        code_base_update = 0

    if metedata_local["version"]["monitorizer"] < metadata_github["version"]["monitorizer"]:
        toolkit_update  = 1
    else:
        toolkit_update  = 0

    if code_base_update == True and toolkit_update == False:
        return templates.help_msg.format( warning0=templates.update_msg.format( metadata_github['changelog']['monitorizer'], warning1="" ))

    if toolkit_update == True and code_base_update == False:
        return templates.help_msg.format( warning0=templates.update_msg.format( metadata_github['changelog']['toolkit'], warning1="" ))

    if toolkit_update == True and code_base_update == True:
        return templates.help_msg.format(
            warning0=templates.update_msg.format( metadata_github['changelog']['monitorizer']),
            warning1=templates.update_msg.format( metadata_github['changelog']['toolkit'])
            )

    return templates.help_msg.format( warning0="" ,warning1="")


def _add(args):
    global watchlist
    alive_targets = []
    for target in args:
        if is_alive(target):
            if not target in watchlist:
                watchlist.append(target)
                alive_targets.append(target)

    open(monitorizer.args.watch , 'w').write('\n'.join(watchlist))
    return "Added {} target(s) to watching list".format(len(alive_targets))

def _remove(args):
    global watchlist
    for target in args:
        if target in watchlist:
            watchlist.remove(target)

    open(monitorizer.args.watch , 'w').write('\n'.join(watchlist))
    return "Removed {} target(s) from watching list".format(len(args))   

def _list(args):
    msg = ""
    for target in [t.strip() for t in open(monitorizer.args.watch,"r").readlines()]:
        msg += templates.target.format(target) + "\n"
    return msg[:-1]

def _ping(args):
    return "pong"




registered_commands = {
    "default": "unrecognized command use @bot help",
    'help':   _help,
    "add":    _add,
    'remove': _remove,
    'list':   _list,
    'ping':   _ping,
}



def mention_handler(data):
    global seen

    if data['event_time'] in seen:
        return "event->app_mention::ignore"

    if len(seen) >= 1000: seen = []

    seen.append(data['event_time'])
    elements   = data["event"]["blocks"][0]["elements"]
    channel_id = data["event"]["channel"]
    message    = []

    for i in range(len(elements)):
        element  = elements[i]["elements"]
        for j in range(len(element)):
            child = element[j]
            if "text" in child:
                message.append( child['text'].strip() )

    if message == []:
        return "event->app_mention::empty_message"

    parent_command    = message[0]
    if len(parent_command) > 1:
        command_arguments = message[1::]
    else:
        command_arguments = []

    if parent_command in registered_commands.keys():
        response = registered_commands[parent_command]
        if type(response) == types.FunctionType:
            response = response(command_arguments)
    else:
        response = registered_commands['default']
        
    monitorizer.slackmsg(response, channel_id)
    
    return "event->app_mention::ok"




@app.route('/slack',methods=['POST'])
def slack_events():
    data = request.json
    if "challenge" in data.keys():
        return data["challenge"]
    return mention_handler(data)


def run_server():
    def _server():
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        app.logger.disabled = True
        logging.getLogger('werkzeug').disabled = True
        os.environ['WERKZEUG_RUN_MAIN'] = 'true'
        app.run(debug=False,port=6969,host='0.0.0.0')
    server = threading.Thread(target=_server)
    server.setDaemon = True
    server.start()
