from .cli import Console
import slack
import yaml

class Report(Console):
    def __init__(self):
        self.slack_token   = None
        self.slack_channel = None

    def local(self,msg,path='results.txt'):
        open(path,"a").write(msg)
        self.log("There was a problem reporting to your slack local save is preformed at results.txt")

    def set_config(self,config_file):
        self.log("Report::config=%s" % config_file)
        self.config        = yaml.safe_load(open(config_file))
        self.slack_channel = self.config['settings']['slack_channel']
        self.slack_token   = self.config['settings']['slack_token']


    def slack(self,msg,channel_id=''):
        client = slack.WebClient(self.slack_token)
        try:
            if not self.slack_token or  not self.slack_channel:
                raise RuntimeError("Couldn't communicate with slack api server(s). please check bot token or channel id")
            response = client.chat_postMessage(channel=self.slack_channel,text=msg)
        except Exception as e:
            self.error(str(e))
            self.local(msg)