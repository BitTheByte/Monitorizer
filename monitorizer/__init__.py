from slackclient import SlackClient
from datetime import datetime
from .helpers import *
import glob


slack_channel = None
slack_token   = None

def set_slack_channel(c):
	global slack_channel
	slack_channel = c
def set_slack_token(t):
	global slack_token
	slack_token = t

def mutliscan(scanners,host,output=""):
	generators = []
	subdomains = []
	for scanner in scanners:
		scanner_start_time = datetime.now()
		generators.append(retattr(
			function = scanner,
			result   = scanner(host))
		)
		scanner_end_time = datetime.now()
		log("<{}> ::: {} Finished, T: {}".format(host,scanner,scanner_end_time - scanner_start_time))

	for generator in generators:
		for subdomain in generator.result:
			if host in subdomain:
				subdomains.append(subdomain.strip().lower())

	open(output,'w').write('\n'.join(subdomains))
	return set(subdomains)

def read_reports(target,exclude=[]):
	result = []
	for path in glob.glob("reports/{}_*".format(target)):
		for e in exclude:
			if e in path:
				break
		else:
			for subdomain in parse(path):
				result.append(subdomain)
	return set(result)

def subfinder(host,threads = 300):
	output  = "temp/%s_subfinder.txt" % host
	osrun(oscmd('subfinder') % (host,output,threads))
	return parse(output)

def dnscan(host,wordlist = "monitorizer/dnscan/subdomains-10000.txt"):
	output   = "temp/%s_dnscan.txt" % host
	osrun(oscmd('dnscan') % (host,wordlist,output))
	return parse(output)

def dnsrecon(host,threads = 100, wordlist = "monitorizer/dnsrecon/subdomains-top1mil.txt"):
	output   = "temp/%s_dnsrecon.txt" % host
	osrun(oscmd('dnsrecon') % (host,wordlist,threads,output))
	return parse(output)

def sublist3r(host,threads = 300):
	output  = "temp/%s_sublist3r.txt" % host
	osrun(oscmd('sublist3r') % (host,output,threads))
	return parse(output)

def subbrute(host):
	output = "temp/%s_subbrute.txt" % host
	osrun(oscmd('subbrute')  % (host,output))
	return parse(output)

def amass(host):
	output = "temp/%s_amass.txt" % host
	osrun(oscmd('amass')  % (host,output))
	return parse(output)

def slackmsg(msg):
	sc = SlackClient(slack_token)
	sc.api_call(
		"chat.postMessage",
		channel=slack_channel,
		text=msg
	)

def clean_temp():
	for i in glob.glob("temp/*"):
		os.unlink(i)

def log(msg):
	msg = "Monitorizer: %s" % msg
	open("log.txt",'a+').write(msg+"\n")
	print(msg)