import requests
import yaml

metadata = {
    "version":{
        "monitorizer": 2.2,
        "toolkit": 1.3
    }
}

try:
    metadata_github = yaml.safe_load(requests.get("https://raw.githubusercontent.com/BitTheByte/Monitorizer/master/version.yaml").text)
except:
    metadata_github = metadata