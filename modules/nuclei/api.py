from modules.report.all import Report
from monitorizer.core.main import Monitorizer
from modules.server.utils import reload_watchlist
from monitorizer.ui.cli import Console
from modules.nuclei.templates import * 
from datetime import datetime
from colorama import Fore
import threading

import subprocess
import needle
import requests
import os
import time



class Nuclei(Report, Monitorizer, Console):
    def __init__(self):
        super().__init__()
    
    def resolve(self, host):
        try:
            url = f"https://{host}"
            requests.get(url, verify=False, timeout=30)
            return url
        except:
            try:
                url = f"http://{host}"
                requests.get(url, verify=False, timeout=30)
                return url
            except:
                pass
        return None

    def same(self, line1, line2):
        if line1 == '' or line2 == '':
            return False
        
        if not ']' in line1 or not ']' in line2:
            return False

        line1 = line1.split("] ", 1)[1]
        line2 = line2.split("] ", 1)[1]

        if line1 == line2:
            return True
        return False


    def compare(self, old_report, new_report):
        new = []
        for new_line in new_report:
            for old_line in old_report:
                if self.same(old_line, new_line):
                    break
            else:
                if new_line.strip():
                    new.append(new_line)
        return new

    def scan(self):
        self.log("started new nuclei scanning thread")

        watchlist  = reload_watchlist()
        subdomains = []
        
        for target in watchlist:
            subdomains += list( self.merge_reports(target) )
        
        report_name   = str(datetime.now().strftime("%Y%m%d_%s"))

        nuclei_input  = "output/nuclei_input_%s" % report_name
        nuclei_output = "reports/nuclei_%s" % report_name

        resolved_subs = set([])

        for cp in needle.GroupWorkers(kernel='threadpoolexecutor', target=self.resolve, arguments=[[sub] for sub in subdomains], concurrent=50):
            if cp._return == None or cp._return == "RUNTIME_ERROR":
                continue
            resolved_subs.add(cp._return)

        open(nuclei_input, 'w').write("\n".join(resolved_subs))


        cmd = f"./modules/nuclei/bin/nuclei -no-color -silent -t modules/nuclei/templates -l {nuclei_input} -o {nuclei_output} {self.nuclei_options}"
        subprocess.check_output(cmd, shell=True)


        old_report = self.merge_reports("nuclei", exclude=[report_name])
        new_report = []
        result     = None

        if os.path.isfile(nuclei_output):
            new_report = open(nuclei_output, 'r').read().split("\n")
            result     = '\n'.join( self.compare(old_report, new_report) )

        if new_report and result.strip():
            self.slack(report_template.format(scan_result=result))

        self.log("nuclei scanning thread finished")
    

    def start_continuous_scanner(self):
        def _continuous():
            while 1:
                self.scan()
                
                if self.nuclei_interval == None:
                    self.nuclei_interval = 24*60*60
                
                self.log(f"nuclei scanning thread is sleeping for {self.nuclei_interval / 60 / 60} hour(s)")
                time.sleep(self.nuclei_interval)

        if self.nuclei_enable == True:
            self.info(f"Continuous scanner is {Fore.GREEN}Enabled")
            thread = threading.Thread(target=_continuous)
            thread.name = "ScannerThread"
            thread.start()
        else:
            self.info(f"Continuous scanner is {Fore.RED}Disabled")