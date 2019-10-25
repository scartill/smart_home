import argparse
import sys
import logging
import threading
import cmd
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib

from aquos import *

SH_WEBHOOK_PORT = 8123
        
class IFTTTWebHook(BaseHTTPRequestHandler):

    commands = {
        "on" : AquosCommander.power_on,
        "off" : AquosCommander.power_off,
        "food" : lambda: AquosCommander.channel("0166"),
        "tlc" : lambda: AquosCommander.channel("0032"),
        "id" : lambda: AquosCommander.channel("0402"),
        "cast" : lambda: AquosCommander.hdmi("0004")
    }

    def do_GET(self):
        url = urllib.parse.unquote(self.path)
        logging.info("Web command: {}".format(url))
        path = url.split('/')
        
        if path[1] != args.token:
            logging.warning("Bad web token: {}".format(path[1]))
            self.send_response(401)
            return
        
        command = str.lower(str.strip(path[2]))
        if not command in IFTTTWebHook.commands:
            logging.warning("Bad IFTTTWebHook command: {}".format(command))
            self.send_response(400)
            return
        
        IFTTTWebHook.commands[command]()
        self.send_response(200)
            
class CmdShell(cmd.Cmd):
    def __init__(self, server):
        super(CmdShell, self).__init__()
        self.server = server
        
    def do_quit(self, arg):
        self.server.shutdown()
        return True

logging.basicConfig(level = logging.DEBUG)
logging.info("Smart Home Hookserver")

parser = argparse.ArgumentParser()
parser.add_argument("token")
parser.add_argument("--interactive", action = "store_true")
args = parser.parse_args()

server = HTTPServer(('0.0.0.0', SH_WEBHOOK_PORT), IFTTTWebHook)

if args.interactive:
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()
    CmdShell(server).cmdloop()
else:
    server.serve_forever()

