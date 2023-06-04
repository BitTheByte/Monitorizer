import os
import re


class ScanParser(object):
    def check(self, domains):
        valid = []
        domains = set(domains)
        regex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9](\.?))$"
        valid.extend(domain for domain in domains if re.search(regex, domain))
        return valid

    def amass(self, data):
        domains = [line.split()[-1].strip() for line in data]
        return self.check(domains)

    def subfinder(self, data):
        domains = [line.strip() for line in data if line[0] != '.']
        return self.check(domains)

    def dnsrecon(self, data):
        domains = [line.split(",")[1] for idx, line in enumerate(data) if idx != 0]
        return self.check(domains)

    def aiodnsbrute(self, data):
        domains = [line.split(",")[0] for idx, line in enumerate(data) if idx != 0]
        return self.check(domains)

    def dnscan(self, data):
        domains = [line.split()[-1].strip() for line in data if '-' in line]
        return self.check(domains)

    def default(self, data):
        domains = [line.strip() for line in data]
        return self.check(domains)

    def parse(self, scan_file):

        if not os.path.isfile(scan_file):
            return []

        data = open(scan_file, 'r').readlines()

        target, tool = os.path.basename(scan_file).split("_")

        if 'amass' in tool:
            return {'amass': self.amass(data)}

        elif 'dnscan' in tool:
            return {'dnscan': self.dnscan(data)}

        elif 'subfinder' in tool:
            return {'subfinder': self.subfinder(data)}

        elif 'dnsrecon' in tool:
            return {'dnsrecon': self.dnsrecon(data)}

        elif 'aiodnsbrute' in tool:
            return {'aiodnsbrute': self.aiodnsbrute(data)}

        return {tool.strip(): self.default(data)}
