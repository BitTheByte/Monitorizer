from datetime import timedelta
from datetime import datetime
from time import sleep
import monitorizer

monitorizer.set_slack_channel("GLDXXXXX")
monitorizer.set_slack_token("xoxb-XXXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXXXXXXXXXX")

scanners = [
	monitorizer.subfinder,
	monitorizer.sublist3r,
	monitorizer.dnsrecon,
	monitorizer.dnscan,
	monitorizer.amass,
]

monitorizer.slackmsg("Monitorizer framework v1 started :tada:")
while 1:
	try:
		for target in [t.strip() for t in open("watch_list","r").readlines()]:
			if not target: break

			report_name = str(datetime.now().strftime("%Y%m%d_%s"))
			report_path = "reports/%s_%s" % (target,report_name)

			monitorizer.log("<{}> ::: {}".format(target,report_path))
			newscan = monitorizer.mutliscan(scanners, target, output=report_path)
			oldscan = monitorizer.read_reports(target,exclude=[report_name])

			if not len(oldscan):
				monitorizer.log("<{}> first Scan".format(target))
				diff = []
			else:
				diff =  newscan - oldscan

			for new in diff:
				monitorizer.log("Found: %s" % new)
				monitorizer.slackmsg(msg="Found: %s " % new)

		monitorizer.clean_temp()
		time = datetime.today()
		future = datetime(time.year,time.month,time.day,2,0)
		if time.hour >= 2:
		    future += timedelta(days=1)
		monitorizer.log("next scan after {} second(s)".format( (future-time).seconds) )
		sleep((future-time).seconds)

	except Exception as e:
		monitorizer.slackmsg("FATEL ERROR: %s" % str(e))

