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
	"dnscan",
	"aiodnsbrute",
	#"amass",
	#"subbrute" - not recommended
]

monitorizer = Monitorizer()
if args.debug == False:
	monitorizer.clear()
events = Events()

if os.path.isfile(args.watch):
	_watch_list = 'set([t.strip() for t in open(args.watch,"r").readlines()])'
	monitorizer.log("Reading targets from file: %s" % args.watch)

else:
	monitorizer.banner()
	monitorizer.error("Couldn't read watch list")
	monitorizer.exit()

monitorizer.set_config(args.config)
events.set_config(args.config)
monitorizer.initialize()
monitorizer.self_check(scanners)
monitorizer.banner()
events.start()


while 1:
	for target in eval(_watch_list):
		flags.status = "running"
		flags.current_target = target

		if not target: continue

		report_name  = str(datetime.now().strftime("%Y%m%d_%s"))
		flags.report_name = report_name
		monitorizer.log("Created new report target=%s name=%s" %(target,report_name))

		current_scan = monitorizer.mutliscan(scanners,target)
		monitorizer.generate_report(target,current_scan,report_name)

		new_domains  = monitorizer.merge_scans(current_scan)
		old_domains  = monitorizer.merge_reports(target,exclude=[report_name])

		if len(old_domains) > 0:
			new_domains = new_domains - old_domains
		else:
			new_domains = []

		for domain in new_domains:
			foundby = []
			for tool,subs in current_scan.items():
				if not domain in subs:
					continue
				foundby.append(tool)
			events.discover(domain,foundby,report_name)

		if args.debug == False:
			monitorizer.clean_temp()

	flags.status = "idle"
	monitorizer.log("Sleeping %i hour(s)" % (flags.sleep_time))
	sleep( 60*60*flags.sleep_time)