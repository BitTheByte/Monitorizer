from slackclient import SlackClient
from colorama import Fore,init
from datetime import datetime
from .functions import *
from .scanner import *
import monitorizer.flags as flags
import dns.resolver
import requests
import random
import glob

metadata = {
    "version":{
        "monitorizer":"1.5",
        "toolkit":"1.1"
    }
}


config  = read_config(args.config)

def metadata_github():
    try:
		return requests.get("https://raw.githubusercontent.com/BitTheByte/Monitorizer/master/version").json()
    except Exception as e:
		print(e)
		return {}


def nxdomain(host):

	"""
		Check for NXDOMAINS  - https://www.dnsknowledge.com/whatis/nxdomain-non-existent-domain-2
	"""
	try:
		dns.resolver.query(host)
		return 0
	except dns.resolver.NXDOMAIN as e:
		return 1

def mutliscan(scanners,target,output=""):

	"""
		Wrapper around scan_with function to scan with multiple tools 
	"""
	subdomains = set()

	for tool in scanners:
		scanner_start_time = datetime.now()

		flags.running_tool   = tool
		flags.current_target = target

		result = scan_with(tool, target)

		scanner_end_time = datetime.now()
		time_taken = (scanner_end_time - scanner_start_time).seconds

		flags.timings[tool] = time_taken


		log("<{}> ::: {} Finished, T: {}".format(target,tool,time_taken))
		
		for subdomain in result:
			if target in subdomain:
				subdomains.add(subdomain.strip().lower())
		


	if output:
		open(output,'w').write('\n'.join(subdomains))

	flags.timings = {}
	return subdomains

def read_reports(target,exclude=[]):

	"""
		Reading reports stored in HOME/reports
	"""
	result = []
	for path in glob.glob("reports/{}_*".format(target)):
		for e in exclude:
			if e in path:
				break
		else:
			for subdomain in parse(path):
				result.append(subdomain)
	return set(result)

def scan_with(name,target):

	"""
		Main scanning function to construct external tools running commands
	"""
	output = "temp/%s_%s" % (target,name)
	if not name in config: return []

	formats = config[name]['formats']
	formats.update({'target':target,'output':output})
	
	cmd = config[name]['cmd'].format(**formats)

	return run_and_return_output(cmd,output)

def slackmsg(msg,channel_id=''):

	"""
		Slack Reporting
	"""

	if local_report:
		open("results.txt","a").write(msg)

	else:

		sc = SlackClient(config['settings']['slack_token'])
		sc.api_call(
			"chat.postMessage",
			channel= channel_id if channel_id else config['settings']['slack_channel'],
			text=msg
		)

def clean_temp():

	"""
		Removes all files at HOME/temp/*
	"""
	for i in glob.glob("temp/*"):
		os.unlink(i)

def log(msg):
	msg = " {r}Monitorizer:{w} {msg}".format(
			b=Fore.BLUE,
			w=Fore.WHITE,
			r=Fore.LIGHTRED_EX,
			msg=msg
		)
	print(msg)

def rand_color():
	return random.choice([
			Fore.RED,
			Fore.GREEN,
			Fore.YELLOW,
			Fore.WHITE,
			Fore.CYAN,
		])

def banner():
	os.system('cls' if os.name == 'nt' else 'clear')
	print ("""
 {r} ___ ___             __ __              __                  
 {r}|   Y   .{w}-----.-----|__|  |_.-----.----|__.-----.-----.----.
 {r}|.      |{w}  _  |     |  |   _|  _  |   _|  |-- __|  -__|   _|
 {r}|. \_/  |{w}_____|__|__|__|____|_____|__| |__|_____|_____|__|  
 {r}|:  |   | {b}The ultimate subdomain monitorization framework                                                 
 {r}|::.|:. |             {y}codebase: v{cversion}, toolkit: v{tversion}                 
 {r}`--- ---'                                                             
                                                             
""".format(
r = Fore.RED,
w = Fore.WHITE,
y = Fore.YELLOW,
g = Fore.GREEN,
b = Fore.LIGHTBLUE_EX,
cversion=metadata["version"]["monitorizer"],
tversion=metadata["version"]["toolkit"],
))

	if local_report:
		log("Slack reporting is disabled due to missing tokens results will be stored at results.txt")

init(autoreset=1)
local_report = False
if not config['settings']['slack_token'] or not config['settings']['slack_channel']:
	local_report = True
	
