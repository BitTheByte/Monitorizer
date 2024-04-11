from pathlib import Path

HOME = Path("/home/.monitorizer")
HOME.mkdir(exist_ok=True)

TEMP = HOME / "tmp"
TEMP.mkdir(exist_ok=True)

WORDLIST = HOME / "wordlist"
WORDLIST.mkdir(exist_ok=True)
