#!/bin/bash

sudo apt-get --assume-yes install git make gcc
mkdir './thirdparty/amass'
mkdir './thirdparty/masscan'
mkdir './nuclei/templates'
git clone https://github.com/blark/aiodnsbrute.git './thirdparty/aiodnsbrute'
git clone https://github.com/aboul3la/Sublist3r './thirdparty/sublist3r'
wget https://github.com/OWASP/Amass/releases/download/v3.21.2/amass_linux_amd64.zip && unzip amass_linux_amd64.zip && cd amass_linux_amd64 && cp amass "../thirdparty/amass/" && cd ..
git clone https://github.com/robertdavidgraham/masscan && cd masscan && make && cp './bin/masscan' '../thirdparty/masscan/masscan' && cd ..
git clone https://github.com/rbsec/dnscan './thirdparty/dnscan'
wget 'https://github.com/projectdiscovery/subfinder/releases/download/v2.5.5/subfinder_2.5.5_linux_amd64.zip' && unzip 'subfinder_2.5.5_linux_amd64.zip' && cp subfinder './thirdparty/subfinder'
wget 'https://github.com/projectdiscovery/nuclei/releases/download/v2.8.9/nuclei_2.8.9_linux_amd64.zip' && unzip 'nuclei_2.8.9_linux_amd64.zip' && mv nuclei './nuclei/bin/nuclei'
nuclei -update-template-dir './nuclei/templates'
rm amass_linux_amd64.zip subfinder_2.5.5_linux_amd64.zip 1.3.2.tar.gz masscan nuclei_2.8.9_linux_amd64.zip -r
pip3 install -r requirements.txt