from core.additional import masscan
from core.globals import metadata
from core.report import Report 
from core.dns import DNS
from core.cli import Console

import events.app_mention as SlackApi


class Events(Report,Console,DNS):
	def discover(self,domain,foundby,report_name):
		
		msg =  "Monitorizer Report ::: %s\n" % report_name
		msg += "[Github]: https://github.com/BitTheByte/Monitorizer\n\n"
		msg +=  "```\n"
		if not self.nxdomain(domain):
			template = "{domain} is found by {foundby} O-Ports:{ports}".format(domain=domain,foundby=foundby,ports=ports)
			
			self.done("Discoverd new subdomain ::  %s" % template)
			ports = masscan(domain)
			msg += template
		msg += "```"
		self.slack(msg=msg)

	def start(self):
		SlackApi.run_server()
		self.done("Started events server at http://0.0.0.0:6500/slack")
		self.slack("Monitorizer framework v{ver} started :tada:".format(ver=metadata["version"]["monitorizer"]))