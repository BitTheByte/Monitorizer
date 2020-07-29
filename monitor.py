from core.monitorizer import Monitorizer
from core.arguments import args
from datetime import timedelta
from datetime import datetime
from events.on import Events
from core import flags
from time import sleep
import os


scanners = [
	"subfinder",
	"sublist3r",
	"dnsrecon",
	"aiodnsbrute",
	"amass",
	# "dnscan", # not as fast as the others
]

monitorizer = Monitorizer()

if args.debug == False:
	monitorizer.clear()

monitorizer.banner()
events = Events()

if os.path.isfile(args.watch):
	_watch_list = 'set([t.strip() for t in open(args.watch,"r").readlines()])'
	monitorizer.log("reading targets from file: %s" % args.watch)

else:
	monitorizer.error("unable to read %s is the file on the disk?" % args.watch)
	monitorizer.exit()


monitorizer.set_config(args.config)
events.initialize()
events.set_config(args.config)
monitorizer.initialize()
monitorizer.self_check(scanners)
events.start()


while 1:
	for target in eval(_watch_list):
		flags.status = "running"
		flags.current_target = target

		if not target.strip(): continue

		report_name  = str(datetime.now().strftime("%Y%m%d_%s"))
		flags.report_name = report_name
		monitorizer.log("created new report target=%s name=%s" %(target,report_name))

		current_scan = monitorizer.mutliscan(scanners,target)
		monitorizer.generate_report(target,current_scan,report_name)

		new_domains  = monitorizer.merge_scans(current_scan)
		old_domains  = monitorizer.merge_reports(target,exclude=[report_name])

		if len(old_domains) > 0:
			new_domains = new_domains - old_domains
		else:
			new_domains = []

		new_domains_filtered = {}
		for domain in new_domains:
			if not domain.strip():
				continue
			foundby = []
			for tool,subs in current_scan.items():
				if not domain in subs:
					continue
				foundby.append(tool)
			new_domains_filtered.update({domain:foundby})

		if new_domains_filtered != {}:
			events.discover(new_domains_filtered,report_name)

		if args.debug == False:
			monitorizer.clean_temp()

	flags.status = "idle"
	monitorizer.done("scanning finished, sleeping for %i hour(s)" % (flags.sleep_time))
	sleep( 60*60*flags.sleep_time)