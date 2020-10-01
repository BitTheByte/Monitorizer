from modules.report.acunetix import AcunetixReport
from modules.report.local import LocalReport
from modules.report.slack import SlackReport
from monitorizer.ui.cli import Console

from monitorizer.ui.arguments import args

import yaml


class Report(Console, LocalReport, SlackReport, AcunetixReport):
    def __get_or_none(self,path):
        result = self.config.copy()
        for root in path.split("."):
            try:
                result = result[root]
            except Exception as e:
                return None
        return result if result == None else result.strip()

    def __init__(self):
        self.config = yaml.safe_load(open(args.config))

        self.slack_channel  = self.__get_or_none("report.slack.channel")
        self.slack_token    = self.__get_or_none("report.slack.token")

        self.acunetix_token = self.__get_or_none("report.acunetix.token")
        self.acunetix_host  = self.__get_or_none("report.acunetix.host")
        self.acunetix_port  = self.__get_or_none("report.acunetix.port")