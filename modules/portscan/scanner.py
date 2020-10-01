import subprocess
import tempfile
import socket
import re
import os


def get_temp_path():
	temp_file = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names())+next(tempfile._get_candidate_names())) 
	if os.path.isfile(temp_file):
		return get_temp_path()
	return temp_file

def _masscan_scan_reader(path):
	if not os.path.isfile(path):
		return "can't find scan file"

	scan_file = open(path,'r').read()
	ports = [x.strip() for x in re.findall(r'portid="(.*?)"', scan_file) if x.strip()]

	if len(ports) == 0:
		return "no open ports"

	return ','.join(ports)

def masscan(target):
	output = get_temp_path()
	try:
		subprocess.check_call(
			"./thirdparty/masscan/masscan {target} -p0-65535 --rate=10000 --open -oX {output}".format(
				output=output,
				target=socket.gethostbyname(target)
			),
			stdout=open(os.devnull, 'a+'),
			stderr=subprocess.STDOUT,
			shell=True
		)
		return _masscan_scan_reader(output)
	except Exception as e:
		return "error"