from core.additional import masscan
from core.globals import metadata
from core.report import Report 
from core.dns import DNS
from core.cli import Console
import events.app_mention as SlackApi


class Events(Report,Console,DNS):
	def initialize(self):
		SlackApi.initialize()

	def discover(self,new_domains,report_name):
		new_domains_filtered = {}
		for domain, foundby in new_domains.items():
			if self.nxdomain(domain) and domain.strip() != '':
				continue
			new_domains_filtered.update({domain:foundby})
		
		if new_domains_filtered == {}:
			return

		msg =  "Monitorizer Report ::: %s\n" % report_name
		msg += "[Github]: https://github.com/BitTheByte/Monitorizer\n\n"
		msg +=  "```\n"
		for domain, foundby in new_domains.items():
			ports = masscan(domain)
			template = "{domain}  by:{foundby} ports:{ports}".format(domain=domain,foundby=', '.join(foundby),ports=ports)
			self.done("Discoverd new subdomain ::  %s" % template)
			msg += template + "\n"
		msg += "```"
		self.slack(msg=msg)

	def start(self):
		SlackApi.run_server()
		self.done("Started events server at http://0.0.0.0:6500/slack")
		self.slack("Monitorizer framework v{ver} started :tada:".format(ver=metadata["version"]["monitorizer"]))
