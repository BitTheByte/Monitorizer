
# Get started
To enable basic slack reporting you need to have:

1. Slack App
    - To create new application to go https://api.slack.com/apps
    - For more information visit https://slack.com/intl/en-eg/blog/productivity/how-to-get-started-building-apps-on-slack

2. Channel ID
    - Open your workspace, click on your channel and look at the url `https://app.slack.com/client/IGNORE/CHANNEL_ID`
      save the last url segment as this will be used later when configuring this tool
 
3. Bot API Token
    - See below 
    

As discussed earlier you need to create a new application and configure it as below:

<p align="center" width="100%">
    <img src=/docs/assets/create_slack_app.PNG width=800px>
</p>


We need to set some permissions inorder to allow the application to send and receive messages from slack, after creating the app you will be greeted with new window. nagivate to the side bar and click on `OAuth & Permissions`

<p align="center" width="100%">
    <img src=/docs/assets/slack_basic_information.PNG width=800px>
</p>

At the same window you should see section called `Scopes` scroll down to it and configure it as below

```
app_mentions:read
chat:write
chat:write.customize
chat:write.public
```
<p align="center" width="100%">
    <img src=/docs/assets/slack_bot_scope.PNG width=500px>
</p>


Nagivate back to the top of the page and install the application to your workspace

<p align="center" width="100%">
    <img src=/docs/assets/slack_oauth.PNG width=700px>
</p>

Back to the same page you should be able to see a new bot token is there. save it as this will be used to configure the application

<p align="center" width="100%">
    <img src=/docs/assets/slack_bot_token.PNG width=700px>
</p>


When finished updated your configuration file located at `config/default.yaml` with the acquired token and channel id. you should be able to receive messages on slack when a new subdomain is found however to control the app using slack you have to enable `App Mentions`

# Enable App Mentions
To enable app mentions you need to go to `Event subscribtion` tab and set `Request URL` to your server hosing the tool

<p align="center" width="100%">
    <img src=/docs/assets/slack_events.PNG width=700px>
</p>

And configure your `bot events` as below

```
app_mention
```
<p align="center" width="100%">
    <img src=/docs/assets/slack_app_mention.PNG width=500px>
</p>

Congratulations you are now ready to go, to verify that eveything is running smoothly navigate to your slack and to your channel then mention the application. if so you should get a response back 

<p align="center" width="100%">
    <img src=/docs/assets/slack_chat_app.PNG width=500px>
</p>
