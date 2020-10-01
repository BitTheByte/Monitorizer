
# Get started
To enable basic slack reporting you need to Go to https://api.slack.com/apps and Create new slack app

![Create Slack App](assets/create_slack_app.PNG)

After creating the app you will be greeted with new window like this. click on `OAuth & Permissions`

![Slack Basic Infromation](assets/slack_basic_information.PNG)

At the `OAuth & Permissions` tab scroll down util you see `Scopes` tab
and set the your bot scopes as follows:

<p align="center" width="100%">
    <img src=/docs/assets/slack_bot_scope.PNG alt="Slack Bot Scope" width=500px>
</p>

```
app_mentions:read
chat:write
chat:write.customize
chat:write.public
```

Scroll up and install the app to your workspace

![Slack Install App](assets/slack_oauth.PNG)

Now the app is installed. set slack bot token on `config/default.yaml` to your token
and to set slack channel just go to your channel and look at the url `https://app.slack.com/client/IGNORE/CHANNEL_ID`

![Slack Bot Token](assets/slack_bot_token.PNG)

Now you will receive new discovered subdomains however to control the app using slack you have to enable app mentions

# Enable App Mentions
To enable app mentions you need to go to `Event subscribtion` tab and set `Request URL` to your server hosing the tool

![Slack Events Subscribtion](assets/slack_events.PNG)

And set your `bot events` as follows


<img src=/docs/assets/slack_app_mention.PNG alt="Slack App Mention Subscribe" width=500px>


```
app_mention
```

Now you're ready to go verify by mentioning the app   

<img src=/docs/assets/slack_chat_app.PNG width=500px>
