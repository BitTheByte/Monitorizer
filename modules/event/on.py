from monitorizer.ui.arguments import args
from monitorizer.ui.cli import Console
from modules.resolvers.dns import DNS
from modules.report.all import Report

from monitorizer.globals import local_metadata
from modules.portscan.scanner import masscan
from monitorizer.core import flags
from modules.server import server
import time


class Events(Report, Console, DNS):
    def exit(self):
        pass

    def scan_start(self, target):
        self.timeings = {target: time.monotonic()}
        self.info(f"Started full scan on {target}")

    def scan_finish(self,target):
        scan_time = round((time.monotonic() - self.timeings[target]) / 60, 3)
        self.info(f"Finished scanning {target}, full scan took: {scan_time} minute(s)")

    def start(self):
        server.run_server()
        self.info(f"Started event server at http://0.0.0.0:{args.port}/slack")
        self.slack(f"Monitorizer framework v{local_metadata['version']['monitorizer']} started :tada:")

    def discover(self, new_domains, report_name):
        new_domains_filtered = {}
        for domain, foundby in new_domains.items():
            if self.nxdomain(domain) and domain.strip() != '':
                continue
            new_domains_filtered.update({domain: foundby})

        if new_domains_filtered == {}:
            return

        msg = f"Monitorizer Report ::: {report_name}\n"
        msg += "[Github]: https://github.com/BitTheByte/Monitorizer\n\n"
        msg += "```\n"
        for domain, foundby in new_domains.items():
            if flags.acunetix:
                self.acunetix(domain)
            ports = masscan(domain)
            template = f"{domain}  by: {', '.join(foundby)} ports: {ports}"
            self.done(f"Discoverd: {template}")
            msg += template + "\n"
        msg += "```"
        self.slack(msg=msg)
