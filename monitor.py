from datetime import timedelta
from datetime import datetime
from handlers import on
from time import sleep
import monitorizer

monitorizer.banner()
monitorizer.first_run()


scanners = [
	"subfinder",
	"sublist3r",
	"dnsrecon",
	"dnscan",
	"amass",
	#"aiodnsbrute" - need to be preinstalled :: python3 -m pip install aiodnsbrute
	#"subbrute" - not recommended
]


if monitorizer.os.path.isfile(monitorizer.args.watch):
	_watch_list = 'set([t.strip() for t in open(monitorizer.args.watch,"r").readlines()])'
	monitorizer.log("Reading targets from file: %s" % monitorizer.args.watch)
else:
	_watch_list = 'set([t.strip() for t in monitorizer.args.watch.split(",")])'
	monitorizer.log("Watching targets: %s" % ','.join(watch_list))

if monitorizer.args.scanners != "all":
	scanners = set([t.strip() for t in monitorizer.args.scanners.split(",")])
	monitorizer.log("Using scanners: %s" % ','.join(scanners))
else:
	monitorizer.log("Using all scanners: %s" % ','.join(scanners))


on.start()

while 1:
	try:
		watch_list = eval(_watch_list)
		for target in watch_list:
			if not target: continue

			report_name = str(datetime.now().strftime("%Y%m%d_%s"))
			report_path = "reports/%s_%s" % (target,report_name)

			monitorizer.log("<{}> ::: {}".format(target,report_path))
			newscan = monitorizer.mutliscan(scanners, target, output=report_path)
			oldscan = monitorizer.read_reports(target,exclude=[report_name])

			if not len(oldscan):
				monitorizer.log("<{}> no previous records".format(target))
				diff = []
			else:
				targets = newscan - oldscan
				if targets: on.discover(targets,report_name)
				
		monitorizer.clean_temp()
		sleep_time_hours = 24
		monitorizer.log("next scan after {} hour(s)".format( sleep_time_hours ))
		sleep( 60*60*sleep_time_hours )

	except Exception as e:
		monitorizer.log("FATEL ERROR: %s" % str(e))
		monitorizer.slackmsg("FATEL ERROR: %s" % str(e))

