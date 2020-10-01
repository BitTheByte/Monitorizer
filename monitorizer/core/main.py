from modules.parsers.scan import ScanParser
from monitorizer.ui.cli import Console

from monitorizer.ui.arguments import args
from monitorizer.core import multitask
from monitorizer.core import flags
from modules.event.on import Events

import subprocess
import platform
import signal
import stat
import yaml
import glob
import os


class Monitorizer(ScanParser, Console):
    def __init__(self):

        self.chmod_tools = [
            './thirdparty/amass/amass',
            './thirdparty/subfinder/subfinder',
            './thirdparty/masscan/masscan'
        ]
        self.create_dirs = ['reports', 'output']
        self.config = None
        self.status = {'running_tools': []}

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

        open('.init', 'w').write('this file is created during first run. please don\'t delete it')

    def exit_code(self, cmd):
        try:
            subprocess.check_output(cmd, stderr=open(os.devnull, 'a+'), shell=True)
            return 0
        except subprocess.CalledProcessError as exc:
            return exc.returncode

    def self_check(self, scanners):
        for tool in scanners:
            health_cmd = self.config[tool]['health']
            if self.exit_code(health_cmd) != 0:
                self.error("Unable to execute %s make sure to install all requirements" % tool)
            else:
                self.log("%s is alive" % tool)

    def install_tools(self, path='thirdparty'):
        pass

    def set_config(self, config_file):
        self.log(f"Monitoizer::config={config_file}")
        try:
            self.config = yaml.safe_load(open(config_file))
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
            self.log("Error occurred during executing :: " + cmd + "\n" + str(e))
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
            os.unlink(i)
        self.log("output/ directory is cleaned")

    def scan_with(self, target, tool_name):
        self.status['running_tools'].append(tool_name)
        flags.running_tool = ', '.join(self.status['running_tools'])

        output = f"output/{target}_{tool_name}"

        if not tool_name in self.config.keys():
            return False

        formats = self.config[tool_name]['formats']
        formats.update({'target': target, 'output': output})
        cmd = self.config[tool_name]['cmd'].format(**formats)

        output = self.run_and_return_output(cmd, output)
        self.status['running_tools'].remove(tool_name)
        self.info(f"{tool_name} finished scanning {target}")
        return output

    def on_scan_finish(self, result):
        _return = result.ret
        if not _return:
            return
        target, tool_name = result.args

        if not target in self.status.keys():
            self.status[target] = {}
        self.status[target].update(_return)

    def mutliscan(self, scanners, target, concurrent=2):
        channel = multitask.Channel()

        for tool in scanners:
            channel.append(target, tool)

        multitask.workers(
            target=self.scan_with,
            channel=channel,
            count=flags.concurrent,
            callback=self.on_scan_finish
        )
        channel.wait()
        channel.close()

        temp = self.status[target]
        del self.status[target]
        return temp


def signal_handler(sig, frame):
    Events().exit()
    os._exit(1)


signal.signal(signal.SIGINT, signal_handler)
