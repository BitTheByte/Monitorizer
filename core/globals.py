import requests

metadata = {
    "version":{
        "monitorizer":"1.6",
        "toolkit":"1.2"
    }
}

metadata_github = requests.get("https://raw.githubusercontent.com/BitTheByte/Monitorizer/master/version").json()