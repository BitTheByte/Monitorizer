from monitorizer.globals import local_metadata
from monitorizer.ui.arguments import args

from colorama import init, Fore

import datetime
import os


class Console(object):
    def time(self):
        return " [%s][" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def log(self, msg):
        if args.verbose == True or args.debug:
            print(self.time() + Fore.LIGHTBLACK_EX + "LOG" + Fore.RESET + "] " + msg.capitalize())

    def info(self, msg):
        print(self.time() + Fore.LIGHTBLUE_EX + "INFO" + Fore.RESET + "] " + msg.capitalize())

    def error(self, msg):
        print(self.time() + Fore.RED + "ERROR" + Fore.RESET + "] " + msg.capitalize())

    def warning(self, msg):
        print(self.time() + Fore.YELLOW + "WARNING" + Fore.RESET + "] " + msg.capitalize())

    def done(self, msg):
        print(self.time() + Fore.GREEN + "SUCCESS" + Fore.RESET + "] " + msg.capitalize())

    def banner(self):
        print(banner_fmt)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def exit(self):
        os._exit(1)


init(autoreset=1)
banner_fmt = """
 {r} ___ ___             __ __              __                  
 {r}|   Y   .{w}-----.-----|__|  |_.-----.----|__.-----.-----.----.
 {r}|.      |{w}  _  |     |  |   _|  _  |   _|  |-- __|  -__|   _|
 {r}|. \_/  |{w}_____|__|__|__|____|_____|__| |__|_____|_____|__|  
 {r}|:  |   | {b}The ultimate subdomain monitorization framework                                                 
 {r}|::.|:. |           {y}codebase: v{cversion}, toolkit: v{tversion}            
 {r}`--- ---'   {b}https://github.com/BitTheByte/Monitorizer                                    
                                              
""".format(
    r=Fore.RED,
    w=Fore.WHITE,
    y=Fore.YELLOW,
    g=Fore.GREEN,
    b=Fore.LIGHTBLUE_EX,
    cversion=local_metadata["version"]["monitorizer"],
    tversion=local_metadata["version"]["toolkit"],
)
