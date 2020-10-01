from monitorizer.ui.arguments import args
import slack


class SlackReport():
    def slack(self, msg, channel_id=''):
        client = slack.WebClient(self.slack_token)
        try:
            if not self.slack_token or not self.slack_channel:
                raise RuntimeError(
                    f"Slack communication is disabled please set slack channel and token at {args.config}")
            response = client.chat_postMessage(channel=self.slack_channel, text=msg)
        except Exception as e:
            self.error(str(e))
            self.local(msg)
