from monitorizer.ui.arguments import args
import yaml


class Config():
    def __get_or_none(self,path):
        result = self.config.copy()
        for root in path.split("."):
            try:
                result = result[root]
            except Exception as e:
                return None
        
        if isinstance(result, str):
            result = result.strip()

        return result 

    def __init__(self):
        self.config = yaml.safe_load(open(args.config))

        self.slack_channel  = self.__get_or_none("report.slack.channel")
        self.slack_token    = self.__get_or_none("report.slack.token")

        self.acunetix_token = self.__get_or_none("report.acunetix.token")
        self.acunetix_host  = self.__get_or_none("report.acunetix.host")
        self.acunetix_port  = self.__get_or_none("report.acunetix.port")


        self.nuclei_interval = self.__get_or_none("settings.nuclei.interval")
        self.nuclei_enable   = self.__get_or_none("settings.nuclei.enable")
        
        self.nuclei_options  = self.__get_or_none("settings.nuclei.options")
