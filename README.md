# Monitorizer
![](https://i.ibb.co/K26yxmB/Untitled-1.png)  
Subdomain monitoring framework inspired by [subalert](https://github.com/yassineaboukir/sublert) project

# Setting up the environment
You need:
- Python  2.7.16
- Linux server e.g(Amanzon EC2)

Before we start you need to install the requirements
```
$ sudo pip install -r requirements.txt
```
After installing the requirements now you're ready to go

# Configuration

This tool requires a slack workspace to report the findings  

You need to edit the `monitor.py` script
```python
monitorizer.set_slack_channel("GLDXXXXX") # change this to your channel id
monitorizer.set_slack_token("xoxb-XXXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXXXXXXXXXX") # change this to your bot user id 
```
For more informations visit: https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens  

  

After editing the python file you just need to edit `watch_list` file to your targets then you're ready to go
```
$ python monitor.py
```
if everything is configured currectly to should see this message on your slack channel
![](https://i.ibb.co/ZMjvTsM/image.png)   

Monitorizer supports more than one subdomain enumeration tool to achieve the best result However you could edit `monitor.py` to add or remove the tools as needed
```python

scanners = [
	monitorizer.subfinder, # https://github.com/subfinder/subfinder
	monitorizer.sublist3r, # https://github.com/aboul3la/Sublist3r
	monitorizer.dnsrecon,  # https://github.com/darkoperator/dnsrecon
	monitorizer.dnscan,    # https://github.com/rbsec/dnscan
	monitorizer.subbrute,  # https://github.com/TheRook/subbrute
	monitorizer.amass,     # https://github.com/OWASP/Amass
]

```
Command lines can be found at `monitorizer/cmd.map`

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
```
$ cat log.txt
```

# TODO
- Windows support
- Config file [Wordlists location / slack token / slack channel id]
- Multithreading support
- Adding more wordlists
- Adding more scanners
