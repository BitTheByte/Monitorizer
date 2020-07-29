from core.globals import metadata,metadata_github
from core.report import Report
from flask import request
from flask import Flask
from . import templates
from . utils import *

import core.flags as flags
import threading
import requests
import logging
import types
import sys
import os
import re



app       = Flask("Slack Events Server")
seen      = []
report    = Report()
watchlist = reload_watchlist()

def initialize():
    report.set_config(argsc.config)

def command_ping(args):
    return "pong"


def command_help(args):
    code_base_update = True if float(metadata["version"]["monitorizer"]) < float(metadata_github["version"]["monitorizer"]) else False
    toolkit_update   = True if float(metadata["version"]["toolkit"]) < float(metadata_github["version"]["toolkit"]) else False

    if code_base_update == True and toolkit_update == False:
        return templates.help_msg.replace("{warning1}\n","").format(
                warning0=templates.update_msg_codebase.format(
                        metadata_github['changelog']['monitorizer']
                )
            )

    if toolkit_update == True and code_base_update == False:
        return templates.help_msg.replace("{warning1}\n","").format(
            warning0=templates.update_msg_toolkit.format(
                    metadata_github['changelog']['toolkit']
                )
            )

    if toolkit_update == True and code_base_update == True:
        return templates.help_msg.format(
                warning0=templates.update_msg_codebase.format(
                        metadata_github['changelog']['monitorizer']
                ),
                warning1=templates.update_msg_toolkit.format(
                    metadata_github['changelog']['toolkit']
                )
            )

    return templates.help_msg.replace("{warning0}\n","").replace("{warning1}\n","")


def command_add(args):
    alive_targets = []
    for target in args:
        if not is_alive(target) or target in watchlist:
            continue

        watchlist.append(target)
        alive_targets.append(target)

    rewrite_watchlist(watchlist)
    return "Added {} target(s) to watching list".format(len(alive_targets))


def command_remove(args):
    for target in args:
        if not target in watchlist:
            continue
        watchlist.remove(target)

    rewrite_watchlist(watchlist)
    return "Removed {} target(s) from watching list".format(len(args))   


def command_list(args):
    msg = ""
    targets = reload_watchlist()
    if len(targets) == 0:
        return "Watchlist is empty"
    for target in targets:
        msg += templates.target.format(target) + "\n"
    return msg[:-1]


def command_freq(args):
    if len(args) == 0:
        return "Scanning frequency is one scan every {} hour(s)".format(flags.sleep_time)

    if str(args[0]).isdigit():
        flags.sleep_time = int(args[0])
        return "Scanning frequency updated to one scan every {} hour(s)".format(args[0])
    else:
        return "Invalid number"

def command_concurrent(args):
    if len(args) == 0:
        return "Concurrent working tools is {}/process".format(flags.concurrent)

    if str(args[0]).isdigit():
        flags.concurrent = int(args[0])
        return "Updated concurrent working tools to {}/process".format(args[0])
    else:
        return "Invalid number"

def command_status(args):
    if flags.status == 'running':
        return templates.run_status_msg.format(
            status         = flags.status,
            target         = flags.current_target,
            tool           = flags.running_tool,
            report_name    = flags.report_name,
            #time_data      = json.dumps(flags.timings, indent=4, sort_keys=True)
        )
    else:
        return templates.stop_status_msg


registered_commands = {
    "default": "unrecognized command use @bot help",
    'help':   command_help,
    "add":    command_add,
    'remove': command_remove,
    'list':   command_list,
    'status': command_status,
    'ping':   command_ping,
    'freq':   command_freq,
    'concurrent': command_concurrent
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

 
    parent_command = message[0]
    if len(message) == 1 and not " " in parent_command:
        parent_command = message[0]
        command_arguments = []
    
    elif " " in parent_command:
        parent_command = parent_command.split(" ")
        if len(parent_command) > 1:
            command_arguments = parent_command[1::]
        else:
            command_arguments = []
        parent_command = parent_command[0]
    else:
        parent_command    = message[0]
        command_arguments = message[1::]

    if parent_command in registered_commands.keys():
        
        response = registered_commands[parent_command]
        if type(response) == types.FunctionType:
            response = response( [i.strip() for i in command_arguments if i.strip()] )
    else:
        response = registered_commands['default']
        
    report.slack(response, channel_id)
    
    return "event->app_mention::ok"


@app.route('/slack',methods=['POST'])
def slack_events():
    data = request.json
    if "challenge" in data.keys():
        return data["challenge"]
    return mention_handler(data)


def run_server():
    def _server():
        if argsc.debug == False:
            cli = sys.modules['flask.cli']
            cli.show_server_banner = lambda *x: None
            app.logger.disabled = True
            logging.getLogger('werkzeug').disabled = True
            os.environ['WERKZEUG_RUN_MAIN'] = 'true'
        app.run(debug=False,port=6500,host='0.0.0.0')
    server = threading.Thread(target=_server)
    server.setDaemon = True
    server.start()
