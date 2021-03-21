from monitorizer.core.main import Monitorizer
from modules.event.on import Events
from modules.nuclei.api import Nuclei

from monitorizer.ui.arguments import args
from monitorizer.core import flags

from datetime import datetime
from time import sleep
import os
import signal


#os._exit(1)

scanners = (
    "subfinder",
    "sublist3r",
    "dnsrecon",
    "aiodnsbrute",
    "amass"
)

monitorizer = Monitorizer()
signal.signal(signal.SIGINT, monitorizer.on_kill)

if not args.debug:
    monitorizer.clear()

monitorizer.banner()
events = Events()
nuclei = Nuclei()

if os.path.isfile(args.watch):
    _watch_list = 'set([t.strip() for t in open(args.watch,"r").readlines()])'
    monitorizer.log(f"reading targets from file: {args.watch}")

else:
    _watch_list = ''  # to make intellisense happy
    monitorizer.error(f"unable to read {args.watch} is the file on the disk?")
    monitorizer.exit()

monitorizer.set_config(args.config)
monitorizer.initialize()
monitorizer.self_check(scanners)
nuclei.start_continuous_scanner()
events.start()


while 1:
    for target in eval(_watch_list):
        flags.status = "running"
        flags.current_target = target

        if not target.strip(): continue

        report_name = str(datetime.now().strftime("%Y%m%d_%s"))
        flags.report_name = report_name
        monitorizer.log(f"created new report target={target} name={report_name}")

        events.scan_start(target)
        current_scan = monitorizer.mutliscan(scanners, target)
        events.scan_finish(target)
        monitorizer.generate_report(target, current_scan, report_name)

        new_domains = monitorizer.merge_scans(current_scan)
        old_domains = monitorizer.merge_reports(target, exclude=[report_name])

        if len(old_domains) > 0:
            new_domains = new_domains - old_domains
        else:
            new_domains = []

        new_domains_filtered = {}
        for domain in new_domains:
            if not domain.strip():
                continue
            foundby = []
            for tool, subs in current_scan.items():
                if not domain in subs:
                    continue
                foundby.append(tool)
            new_domains_filtered.update({domain: foundby})

        if new_domains_filtered != {}:
            events.discover(new_domains_filtered, report_name)

        #if not args.debug:
        #    monitorizer.clean_temp()

    flags.status = "idle"
    monitorizer.info(f"All targets scanned, sleeping for {flags.sleep_time} hour(s)")
    sleep(60 * 60 * flags.sleep_time)