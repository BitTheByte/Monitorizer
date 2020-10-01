import argparse

parser = argparse.ArgumentParser(description='Welcome to monitorizer help page')
group = parser.add_argument_group('required arguments')

group.add_argument('-w','--watch',type=str, help='Watching List File | -w /path/to/file.txt' ,required=True)
parser.add_argument('-s','--scanners',type=str, help='Set Scanners | -s subfinder,amass',default='all')
parser.add_argument('-c','--config',type=str, help='Config Path | -c config.json',default='config/default.yaml')
parser.add_argument('-p','--port',type=int, help='Port for Events server',default=6500)
parser.add_argument('-v','--verbose', help='Enable verbose options',action='store_true')
parser.add_argument('-d','--debug', help='Enable stdout for tools',action='store_true')


args = parser.parse_args()