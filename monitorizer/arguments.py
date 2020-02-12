import argparse

parser = argparse.ArgumentParser(description='Welcome to monitorizer help page')
group = parser.add_argument_group('required arguments')

group.add_argument('-w','--watch',type=str, help='Watching List File | -w /path/to/file.txt' ,required=True)
parser.add_argument('-s','--scanners',type=str, help='Set Scanners | -s subfinder,amass',default='all')
parser.add_argument('-c','--config',type=str, help='Config Path | -c config.json',default='config/default.json')

args = parser.parse_args()