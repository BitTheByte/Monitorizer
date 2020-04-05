import requests

metadata = {
    "version":{
        "monitorizer":"2.0",
        "toolkit":"1.2"
    }
}

metadata_github = requests.get("https://raw.githubusercontent.com/BitTheByte/Monitorizer/master/version").json()