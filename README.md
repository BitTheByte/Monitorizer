# xElkomy how to use

You need to run this script `bash install.sh` and it will install the required tools.

# Monitorizer

<p align="center">
    <a href="https://twitter.com/BitTheByte">
      <img src="https://i.ibb.co/9pYWyKR/68747470733a2f2f692e6962622e636f2f775367634b66782f417274626f6172642d312e706e67.png" width="500">
    </a>
    <h3 align="center">The ultimate subdomain monitorization framework</h3>
</p>

Subdomain monitoring framework inspired by [subalert](https://github.com/yassineaboukir/sublert) project

# Scanners integration

- Nuclei integration

  - This integration is enabled by default with no action from the user however if you wish to disable it or modify it's options edit `config/default.yaml`

  - An always running instance of `projectdiscovery/nuclei` that will scan ALL (not just the newly found) subdomains from targets in the watch list - only modify the watch list from slack commands e.g `@monitorizer add example.com`

  - Keep in mind you're responsible for updating your local copy of nuclei templates at `modules/nuclei` from https://github.com/projectdiscovery/nuclei-templates

- Acunetix integration

  - This integration is disabled by default you must send `@monitorizer acunetix enable` to your running monitorizer instance to enable this integration

  - You need to have your own Acunetix instance

  - On a newly discovered subdomain this integration will start new Acunetix scan

# Setting up the environment

You need:

- Python >= 3.6 ( python 2 is not supported )
- Linux server e.g(Amanzon EC2) [64bit]

Before we start you need to install the requirements

```
$ sudo pip3 install -r requirements.txt
```

After installing the requirements now you're ready to go

# Configuration

This tool requires a slack workspace to report the findings. Additionally you can use the included acunetix integration to scan the newly discoverd domains

You need to edit the `config/default.yaml`

```yaml
report:
  slack: # required
    channel: CM8XXXXXX
    token: xoxb-XXXXXXXXXX-ZZZZZZZZZZ-YYYYYYYYYYYYYY

  acunetix: # optional
    token: 63c19a6da79816b21429e5bb262daed863c19a6da79816b21429e5bb262daed8
    host: acunetix.exmaple.com
    port: 3443

settings:
  nuclei:
    enable: true
    interval: 86400 # rescan all targets in the watch list every 24h
    options: -impact high
```

For more information see: [docs/get_started.md](/docs/get_started.md)

```
$ python monitor.py -w watch_targets.txt
```

if everything is configured currectly to should see this message on your slack channel
![](https://i.ibb.co/ZMjvTsM/image.png)

Monitorizer supports more than one subdomain enumeration tool to achieve the best result

```python

scanners = [
	aiodnsbrute, # https://github.com/blark/aiodnsbrute (included)
	subfinder,   # https://github.com/subfinder/subfinder (included)
	sublist3r,   # https://github.com/aboul3la/Sublist3r (included)
	dnsrecon,    # https://github.com/darkoperator/dnsrecon (included)
	dnscan,      # https://github.com/rbsec/dnscan (included)
	amass,       # https://github.com/OWASP/Amass (included)
]

```

command lines can be found at `config/default.yaml`
It is also recommended to add your API keys in the `config/thirdparty/*`

# How to run

As the script runs once everyday to need to host it on a running linux server

```
$ ssh myserver@somewhere.host
$ ls
Monitorizer
$ cd Monitorizer
$ screen -dmS monitorizer bash -c 'python3 monitor.py -w targets.txt'
```

# Slack Commands

Monitorizer supports slack commands by mentioning the bot

![](https://i.ibb.co/NFL2N7r/image.png)

To Enable Slack commands you have to enable [Event Subscriptions](https://api.slack.com/events-api) and set the [Request URL] to http://your_ip:6500/slack

| Command    | Description                                               | Usage                                                                          |
| ---------- | --------------------------------------------------------- | ------------------------------------------------------------------------------ |
| list       | Lists all targets                                         | @monitorizer list                                                              |
| add        | Adds new target                                           | @monitorizer add target.com or @monitorizer add target1.com, target2.com       |
| remove     | Remove targets                                            | @monitorizer remove target.com or @monitorizer remove target1.com, target2.com |
| ping       | Health check for the server                               | @monitorizer ping                                                              |
| status     | Prints the current status                                 | @monitorizer status                                                            |
| concurrent | Set/Get number of concurrent scanners                     | @monitorizer concurrent or @monitorizer concurrent {number}                    |
| acunetix   | Enabled/Disable sending new discoverd targets to acunetix | @monitorizer acunetix enable or @monitorizer acunetix disable                  |
| freq       | Set/Get scan frequency (in hours)                         | @monitorizer freq or @monitorizer freq {number}                                |

# FAQ

1. Scanning may hang on some targets for a long time

   - Try running the tool with `-d` flag to debug the problem
   - Edit the `timeout` flag at `config/default.yaml` to your desired time in **seconds**

2. Slack's bot app don't respond to my commands
   - Check your slack bot token
   - Reconfigure the tool using the [docs](/docs/get_started.md)

# TODO

Full todo list is at https://github.com/BitTheByte/Monitorizer/projects/1
