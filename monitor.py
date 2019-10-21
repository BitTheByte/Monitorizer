from datetime import timedelta
from datetime import datetime
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
	watch_list = set([t.strip() for t in open(monitorizer.args.watch,"r").readlines()])
	monitorizer.log("Reading targets from file: %s" % monitorizer.args.watch)
else:
	watch_list = set([t.strip() for t in monitorizer.args.watch.split(",")])
	monitorizer.log("Watching targets: %s" % ','.join(watch_list))

if monitorizer.args.scanners != "all":
	scanners = set([t.strip() for t in monitorizer.args.scanners.split(",")])
	monitorizer.log("Using scanners: %s" % ','.join(scanners))
else:
	monitorizer.log("Using all scanners: %s" % ','.join(scanners))


monitorizer.slackmsg("Monitorizer framework v1.1 started :tada:")

while 1:
	try:
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
				diff =  newscan - oldscan

			for new in diff:
				if not monitorizer.nxdomain(new):
					monitorizer.log("new subdomain: %s" % new)
					monitorizer.slackmsg(msg="Found: %s " % new)

		monitorizer.clean_temp()
		time = datetime.today()
		future = datetime(time.year,time.month,time.day,2,0)
		if time.hour >= 2:
		    future += timedelta(hours=8)
		monitorizer.log("next scan after {} hour(s)".format( int(float((future-time).seconds)/60/60)) )
		sleep((future-time).seconds)

	except Exception as e:
		monitorizer.log("FATEL ERROR: %s" % str(e))
		monitorizer.slackmsg("FATEL ERROR: %s" % str(e))