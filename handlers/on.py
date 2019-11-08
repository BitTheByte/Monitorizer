import monitorizer

def discover(targets,report_name):
	msg =  "Monitorizer Report ::: %s\n" % report_name
	msg += "[Github]: https://github.com/BitTheByte/Monitorizer\n\n"
	msg +=  "```\n"
	for subdomain in targets:
		if not monitorizer.nxdomain(subdomain):
			ports = monitorizer.masscan(subdomain)
			monitorizer.log("found: {subdomain} {ports}".format(subdomain=subdomain,ports=ports))
			msg += "{subdomain} {ports} \n".format(subdomain=subdomain,ports=ports)
	msg += "```"
	monitorizer.slackmsg(msg=msg)

def start():
	monitorizer.slackmsg("Monitorizer framework v1.2 started :tada:")