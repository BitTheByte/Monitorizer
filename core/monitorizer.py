from .parser import ScanParser
from .cli import Console
from . import multitask
import json
import glob
import subprocess
import subprocess
import platform
import signal
import requests
import json
import stat
import sys
import os
from . import flags
from .arguments import args


class Monitorizer(ScanParser,Console):
    def __init__(self):

        self.chmod_tools = [
            './thirdparty/amass/amass',
            './thirdparty/subfinder/subfinder',
            './thirdparty/masscan/masscan'
        ]
        self.create_dirs = [
            'reports',
            'temp'
        ]

        self.config  = None
        self.memsave = {'running_tools':[]}

    def initialize(self):
        if not self.iscompatible():
            self.error("Your OS is not compatible with this tool. running it as root may fix the problem ")
            self.exit()

        if os.path.isfile('.init'):
            self.log(".init file is found.. skipping initialization process")
            return 
    
        self.warning("Monitoizer is initializing please don't interrupt ..")
        self.init_dirs()
        self.set_permissions()
        self.install_tools()

        open('.init','w').write('true')

    def exit_code(self,cmd):
        try:
            subprocess.check_output(cmd, stdout=open(os.devnull,'a+'),stderr=subprocess.STDOUT,shell=True)
            return 0
        except subprocess.CalledProcessError as exc:
            return exc.returncode

    def self_check(self,scanners):
        for tool in scanners:
            health_cmd = self.config[tool]['health']
            if self.exit_code(health_cmd) != 0:
                self.error("Unable to execute %s make sure to install all requirements" % tool)
            else:
                self.log("%s is alive" % tool)

    def install_tools(self,path='thirdparty'):
        pass

    def set_config(self,config_file):
        self.log("Monitoizer::config=%s" % config_file)
        try:
            self.config = json.loads(open(config_file,'r').read())
        except Exception as e:
            self.error(e)
        
    def iscompatible(self):
        if platform.architecture()[0].lower() != '64bit':
            self.log("64bit CPU was expected")
            return False
        if os.geteuid() != 0:
            self.log("Tool is not running as root")
            return False
        return True

    def init_dirs(self):
        for dir_name in self.create_dirs:
            if os.path.isdir(dir_name): continue
            os.mkdir(dir_name)
            self.log("Created new directory :: %s" % dir_name)

    def set_permissions(self):
        for tool in self.chmod_tools:
            st = os.stat(tool)
            os.chmod(tool, st.st_mode | stat.S_IEXEC)
            self.log("Changed permissions of %s" % tool)

    def run_and_return_output(self,cmd,output,silent=0):
        self.log("Running command :: " + cmd)
        try:
            if not args.debug:
                subprocess.check_call(cmd,stdout=open(os.devnull,'a+'),stderr=subprocess.STDOUT,shell=True)
            else:
                subprocess.check_call(cmd,shell=True)
            return self.parse( output )
        except Exception as e:
            self.log("Error occurred during executing :: " + cmd + "\n" + str(e))
            return False

    def merge_reports(self,target,exclude=[]):
        result = []
        for path in glob.glob("reports/{}_*".format(target)):
            for e in exclude:
                if path == "reports/%s_%s" % (target,e):
                    break
            else:
                for subdomain in open(path,'r').read().split('\n'):
                    result.append(subdomain)
        return set(result)

    def merge_scans(self,scan):
        domains = set()
        for tool,subs in scan.items():
            for sub in subs:
                domains.add(sub)
        return domains

    def generate_report(self,target,scan,suffix=''):
        domains = self.merge_scans(scan)
        report = 'reports/%s_%s' % (target,suffix)
        open(report,'w').write('\n'.join(domains))
        return report

    def clean_temp(self):
        for i in glob.glob("temp/*"):
            os.unlink(i)
        self.log("temp/ directory is cleaned")

    def scan_with(self,target,tool_name):
        self.memsave['running_tools'].append(tool_name)
        flags.running_tool = ', '.join(self.memsave['running_tools'])

        output = "temp/%s_%s" % (target,tool_name)

        if not tool_name in self.config.keys():
            return False 

        formats = self.config[tool_name]['formats']
        formats.update({'target':target,'output':output})
        cmd = self.config[tool_name]['cmd'].format(**formats)

        output = self.run_and_return_output(cmd,output)
        self.memsave['running_tools'].remove(tool_name)
        self.done("%s finished scanning %s" % (tool_name,target))
        return output

    def on_scan_finish(self,result):
        _return = result.ret
        if _return == False:
            return
        target,tool_name = result.args

        if not target in self.memsave.keys():
            self.memsave[target] = {}
        self.memsave[target].update(_return)

    def mutliscan(self,scanners,target,concurrent=2):
        subdomains = set()
        channel    = multitask.Channel()

        for tool in scanners:
            channel.append(target,tool)

        multitask.workers(
            target=self.scan_with,
            channel=channel,
            count=flags.concurrent,
            callback=self.on_scan_finish
        )
        channel.wait()
        channel.close()

        temp = self.memsave[target]
        del self.memsave[target]
        return temp

def signal_handler(sig, frame):
    os._exit(1)

signal.signal(signal.SIGINT, signal_handler)