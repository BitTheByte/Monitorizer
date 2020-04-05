from .cli import Console
import slack
import json

class Report(Console):
    def __init__(self):
        self.slack_token   = None
        self.slack_channel = None

    def local(self,msg,path='results.txt'):
        open(path,"a").write(msg)
        self.log("There was a problem reporting to your slack local save is preformed at results.txt")

    def set_config(self,config_file):
        self.log("Report::config=%s" % config_file)
        self.config        = json.loads(open(config_file,'r').read())
        self.slack_channel = self.config['settings']['slack_channel']
        self.slack_token   = self.config['settings']['slack_token']


    def slack(self,msg,channel_id=''):
        client = slack.WebClient(self.slack_token)

        try:
            if not self.slack_token or  not self.slack_channel:
                raise RuntimeError("Slack API are not set")

            response = client.chat_postMessage(channel=self.slack_channel,text=msg)
        except Exception as e:
            print(e)
            self.local(msg)