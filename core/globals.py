import requests

metadata = {
    "version":{
        "monitorizer":"2.1",
        "toolkit":"1.2"
    }
}

try:
    metadata_github = requests.get("https://raw.githubusercontent.com/BitTheByte/Monitorizer/master/version").json()
except:
    metadata_github = metadata