import os
import re


class ScanParser(object):
    def check(self, domains):
        valid = []
        domains = set(domains)
        regex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9](\.?))$"
        for domain in domains:
            if not re.search(regex, domain): continue
            valid.append(domain)
        return valid

    def amass(self, data):
        domains = []
        for line in data:
            domains.append(line.split()[-1].strip())
        return self.check(domains)

    def subfinder(self, data):
        domains = []
        for line in data:
            if line[0] == '.':
                continue
            domains.append(line.strip())
        return self.check(domains)

    def dnsrecon(self, data):
        domains = []
        for idx,line in enumerate(data):
            if idx == 0:
                continue
            domains.append(line.split(",")[1])
        return self.check(domains)

    def aiodnsbrute(self, data):
        domains = []
        for idx,line in enumerate(data):
            if idx == 0:
                continue
            domains.append(line.split(",")[0])
        return self.check(domains)

    def dnscan(self, data):
        domains = []
        for line in data:
            if not '-' in line:
                continue
            domains.append(line.split()[-1].strip())
        return self.check(domains)

    def default(self, data):
        domains = []
        for line in data:
            domains.append(line.strip())
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
