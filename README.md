# Monitorizer
![](https://i.ibb.co/wSgcKfx/Artboard-1.png)  
Subdomain monitoring framework inspired by [subalert](https://github.com/yassineaboukir/sublert) project

# Setting up the environment
You need:
- Python  2.7.16
- Linux server e.g(Amanzon EC2) [64bit]

Before we start you need to install the requirements
```
$ sudo pip install -r requirements.txt
```
After installing the requirements now you're ready to go

# Configuration

This tool requires a slack workspace to report the findings  

You need to edit the `config/default.json` 
```json

{
	"settings":{
		"slack_channel":"change this to your channel id",
		"slack_token":"change this to your bot user Oauth token",
	}
}
```
For more informations visit: https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens  

  

```
$ python monitor.py -w google.com,bing.com
```
```
$ python monitor.py -w watch_targets.txt
```
if everything is configured currectly to should see this message on your slack channel
![](https://i.ibb.co/ZMjvTsM/image.png)   

Monitorizer supports more than one subdomain enumeration tool to achieve the best result
```python

scanners = [
	aiodnsbrute, # https://github.com/blark/aiodnsbrute (need to be installed)
	subfinder,   # https://github.com/subfinder/subfinder (included)
	sublist3r,   # https://github.com/aboul3la/Sublist3r (included)
	dnsrecon,    # https://github.com/darkoperator/dnsrecon (included)
	dnscan,      # https://github.com/rbsec/dnscan (included)
	subbrute,    # https://github.com/TheRook/subbrute (included)
	amass,       # https://github.com/OWASP/Amass (included)
]

```
command lines can be found at `config/default.json`

# How to run

As the script runs once everyday to need to host it on a running linux server
```
$ ssh myserver@somewhere.host
$ ls
Monitorizer
$ cd Monitorizer
$ screen -dmS monitorizer bash -c 'python monitor.py'
```

Now monitorizer should be working at the background to view the logs just run

# ChangeLog
```
1.0: untracked
1.1: untracked
1.2: 
  - Added: New events system  
  - Added: Support for masscan
  - Improved: Slack reporting system 
```

# TODO
- Windows support
- Multithreading support
- Adding more scanners
