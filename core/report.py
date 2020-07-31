from .cli import Console
from .acunetix import Acunetix
import slack
import yaml

class Report(Console):
    def __init__(self):
        self.slack_token    = None
        self.slack_channel  = None
        self.acunetix_token = None
        self.acunetix_host  = None
        self.acunetix_port  = None

    def local(self,msg,path='results.txt'):
        open(path,"a").write(msg + "\n")
        self.log("There was a problem reporting to your slack local save is preformed at results.txt")

    def set_config(self,config_file):
        self.log("Report::config=%s" % config_file)
        self.config         = yaml.safe_load(open(config_file))
        self.slack_channel  = self.config['settings']['slack_channel']
        self.slack_token    = self.config['settings']['slack_token']
        self.acunetix_token = self.config['settings']['acunetix_token']
        self.acunetix_host  = self.config['settings']['acunetix_host']
        self.acunetix_port  = int(self.config['settings']['acunetix_port'])

    def slack(self,msg,channel_id=''):
        client = slack.WebClient(self.slack_token)
        try:
            if self.slack_token == 'xxxxxxxxxxx' or  self.slack_channel == 'xxxxxxxxxxx':
                raise RuntimeError("unable to communicate with slack api server(s). please check bot token or channel id")
            response = client.chat_postMessage(channel=self.slack_channel,text=msg)
        except Exception as e:
            self.error(str(e))
            self.local(msg)

    def acunetix(self,target):
        if self.acunetix_host == 'example.com' or self.acunetix_token == 'xxxxxxxxxxx':
            msg = "disabled acunetix integration due to missing configurations"
            self.log(msg)
            self.local(msg)
            return 

        try:
            acunetix = Acunetix(host="%s:%i" % (self.acunetix_host,self.acunetix_port),api=self.acunetix_token)
            acunetix.start_scan(target.strip())
            self.log("created new acunetix's scan target="+target)
        except Exception as e:
            self.slack("acunetix integration had an error: " + str(e))
        