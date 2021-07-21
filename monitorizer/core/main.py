import sys
import os

if sys.path[0] != os.getcwd():
    print("Relative run is not supported for compatibility reasons")
    print(f'Please go to "{sys.path[0]}" and run the tool')
    os._exit(1)

from modules.parsers.scan import ScanParser
from monitorizer.ui.cli import Console

from monitorizer.ui.arguments import args
from monitorizer.core import flags
from modules.event.on import Events

from wrapt_timeout_decorator import *
import subprocess
import platform
import signal
import stat
import yaml
import glob
import needle



class Monitorizer(ScanParser, Console):
    def __init__(self):
        self.chmod_tools = [
            './thirdparty/amass/amass',
            './thirdparty/subfinder/subfinder',
            './thirdparty/masscan/masscan',
            './modules/nuclei/bin/nuclei'
        ]
        self.create_dirs = ['reports', 'output']
        self.config = None
        self.scan_timeout = 0
        self.progress = {'running_tools': [], "formated_cmds": []}

    def initialize(self):
        if not self.iscompatible():
            self.error("Your OS is not compatible with this tool. running it as root may fix the problem ")
            self.exit()

        if os.path.isfile('.init'):
            self.log("Skipping first run initialization process")
            return

        self.warning("Monitonizer is initializing, Please don't interrupt")
        self.init_dirs()
        self.set_permissions()
        self.install_tools()

        open('.init', 'w').write('this file is created during first run. please don\'t delete it')

    def exit_code(self, cmd):
        try:
            subprocess.check_output(cmd, stderr=open(os.devnull, 'a+'), shell=True)
            return 0
        except subprocess.CalledProcessError as exc:
            return exc.returncode

    def self_check(self, scanners):
        for tool in scanners:
            toolconfig = self.config.get(tool, None)
            if toolconfig == None:
                continue
            health_cmd = toolconfig['health']
            if self.exit_code(health_cmd) != 0:
                self.error("Unable to execute %s make sure to install all requirements" % tool)
            else:
                self.log(f"Started {tool} without any errors/problems")

    def install_tools(self, path='thirdparty'):
        pass

    def set_config(self, config_file):
        self.log(f"Monitonizer::config={config_file}")
        try:
            self.config = yaml.safe_load(open(config_file))
            self.scan_timeout = self.config["settings"]["scan"]["timeout"]
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
            self.log(f"Created new directory :: {dir_name}")

    def set_permissions(self):
        for tool in self.chmod_tools:
            st = os.stat(tool)
            os.chmod(tool, st.st_mode | stat.S_IEXEC)
            self.log(f"Changed permissions of {tool}")

    def run_and_return_output(self, cmd, output, silent=0):
        self.log("Running command :: " + cmd)
        try:
            if not args.debug:
                subprocess.check_call(cmd, stdout=open(os.devnull, 'a+'), stderr=subprocess.STDOUT, shell=True)
            else:
                subprocess.check_call(cmd, shell=True)
            return self.parse(output)
        except Exception as e:
            self.log("Error occurred during executing :: " + cmd + " - " + str(e))
            return False

    def merge_reports(self, target, exclude=[]):
        result = []
        for path in glob.glob(f"reports/{target}_*"):
            for e in exclude:
                if path == f"reports/{target}_{e}":
                    break
            else:
                for subdomain in open(path, 'r').read().split('\n'):
                    result.append(subdomain)
        return set(result)

    def merge_scans(self, scan):
        domains = set()
        for tool, subs in scan.items():
            for sub in subs:
                domains.add(sub)
        return domains

    def generate_report(self, target, scan, suffix=''):
        domains = self.merge_scans(scan)
        report = f'reports/{target}_{suffix}'
        open(report, 'w').write('\n'.join(domains))
        return report

    def clean_temp(self):
        for i in glob.glob("output/*"):
            if "keep-" in i:
                continue
            os.unlink(i)
        self.log("output/ directory is cleaned")

    def pids_by_cmd(self, cmd):
        pids = []
        ps = subprocess.check_output(["ps -o pid,command"], shell=True).decode().split("\n")
        for running_cmd in ps:
            if cmd in running_cmd:
                pid = int([i for i in running_cmd.split(" ") if i.isdigit()][0])
                pids.append(pid)
        return pids

    def kill_by_cmd(self, cmd):
        killed = []
        for pid in self.pids_by_cmd(cmd):
            os.kill(pid, signal.SIGKILL)  # aggressive but useful :)
            killed.append(str(pid))
        self.info(f"Killed process(es): {', '.join(killed)}")

    def fmt_cmd(self, tool_name, target):
        formats = self.config[tool_name]['formats']
        output = f"output/{target}_{tool_name}"
        formats.update({'target': target, 'output': output})
        cmd = self.config[tool_name]['cmd'].format(**formats)
        self.progress["formated_cmds"].append(cmd)
        return cmd, output

    def scan_with(self, target, tool_name):

        @timeout(self.scan_timeout)
        def timed_scan(target, tool_name):
            self.progress['running_tools'].append(tool_name)
            flags.running_tool = ', '.join(self.progress['running_tools'])

            if not tool_name in self.config.keys():
                return False

            cmd, output = self.fmt_cmd(tool_name, target)
            output = self.run_and_return_output(cmd, output)
            self.progress['running_tools'].remove(tool_name)

            flags.running_tool = ', '.join(self.progress['running_tools'])
            self.info(f"{tool_name} finished scanning {target}")
            return output

        try:
            return timed_scan(target, tool_name)
        except:
            self.error(
                f"Maximum execution time of {self.scan_timeout} second(s) reached while running {tool_name} on {target}")
            cmd, output = self.fmt_cmd(tool_name, target)
            self.kill_by_cmd(cmd)
            return {"error": "timeout"}


    def mutliscan(self, scanners, target, concurrent=None):
        for res in needle.GroupWorkers(kernel='threadpoolexecutor', target=self.scan_with, arguments=[(target, tool) for tool in scanners], concurrent=flags.concurrent):
            if res._return == "RUNTIME_ERROR" or not res._return:
                continue

            _return = res._return
            target, tool_name = res.arguments

            if not target in self.progress.keys():
                self.progress[target] = {}
            
            self.progress[target].update(_return)

        temp = self.progress[target]
        del self.progress[target]
        return temp


    def on_kill(self, sig, frame):
        Events().exit()
        pids = []
        delay = 10
        for cmd in self.progress["formated_cmds"]:
            pids += self.pids_by_cmd(cmd)
            for pid in pids:
                # Yes yes, it's vulnerable to time of check time of use attack
                # However I don't think it's that high chance of it to happen if not exploited intentionally
                # If you have a better idea to do this please make a PR. Thanks :)
                subprocess.Popen(f"sleep {delay}; kill -9 {pid} > /dev/null 2>&1", start_new_session=True, shell=True)
            delay += 1
        self.info("Initiated exit procedure, sub-process(es) will exit soon .. bye!")
        os._exit(1)
