from monitorizer.ui.arguments import args
import slack
import time

class SlackReport():
    def slack(self, msg, channel_id=''):
        client = slack.WebClient(self.slack_token)
        
        for _ in range(10):
            try:
                if not self.slack_token or not self.slack_channel:
                    raise RuntimeError(
                        f"Slack communication is disabled please set slack channel and token at {args.config}")
                response = client.chat_postMessage(channel=self.slack_channel, text=msg)
                return
            except Exception as e:
                self.error(str(e))
         
            time.sleep(30)
        
        self.local(msg)