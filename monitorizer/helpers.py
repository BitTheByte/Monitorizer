import subprocess
import os

class obj(object):
	pass
def retattr(**kwargs):
	o = obj()
	for key,val in kwargs.items():
		setattr(o, key, val)
	return o

def osrun(cmd):
	#print cmd
	#subprocess.call(cmd,shell=True)
	subprocess.call(cmd,stdout=open(os.devnull, 'w'),stderr=subprocess.STDOUT,shell=True)

def oscmd(tool):
	for i in open('monitorizer/cmd.map','r').readlines():
		if tool in i.split(":")[0]:
			return i.split(":")[1].strip()

def parse(filepath):
	data = open(filepath,'r').readlines()
	if 'amass' in filepath:
		for line in data:
			domain = line.split()[-1].strip()
			if domain: yield domain

	elif 'dnscan' in filepath:
		for line in data:
			if '-' in line:
				domain = line.split()[-1].strip()
				if domain: yield domain

	elif 'subfinder' in filepath:
		for line in data:
			if line[0] != '.':
				yield line.strip()
	elif 'dnsrecon' in filepath:
		for line in data:
			if not 'Name' in line:
				yield line.split(",")[1]

	else:
		for line in data:
			if line.strip():
				yield line.strip()