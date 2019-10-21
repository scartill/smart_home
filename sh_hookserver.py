import argparse
import sys
import socket
import logging
import threading
import cmd
from http.server import BaseHTTPRequestHandler, HTTPServer

SH_WEBHOOK_PORT = 8123

AQUOS_TCP_IP = '192.168.0.107'
AQUOS_TCP_PORT = 10002
RVC_BUFFER_SIZE = 1024

class AquosControl(object):
    def __init__(self):
        self.sock = None
        
    def __enter__(self): 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((AQUOS_TCP_IP, AQUOS_TCP_PORT))
        return self
  
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.sock.close()
        
    def send_command(self, command, param):
        full_command = bytearray(command + param, 'ascii')
        full_command.append(0x0D)
        
        if self.sock != None:
            self.sock.send(full_command)
            data = self.sock.recv(RVC_BUFFER_SIZE)
            logging.info("Received: " + str(data))
        
    def send_bool(self, command, onoff):
        if onoff:
            param = "0001"
        else:
            param = "0000"
            
        self.send_command(command, param)       
            
class AquosCommander:
    def power_off():
        with AquosControl() as ac:
            ac.send_bool("RSPW", True)
            ac.send_bool("POWR", False)
    
    def power_on():
        with AquosControl() as ac:
            ac.send_bool("RSPW", True)
            ac.send_bool("POWR", True)
    
    def channel(channel):
        with AquosControl() as ac:
            ac.send_command("DTVD", channel)
        
        
class IFTTTWebHook(BaseHTTPRequestHandler):
    def do_GET(self):
        response = 200
                
        if self.path == "/{}/on".format(args.token):
            AquosCommander.power_on()            
        elif self.path == "/{}/off".format(args.token):
            AquosCommander.power_off()            
        else:
            logging.warning("Unknown web command")
            response = 404
        
        self.send_response(response)
            
class CmdShell(cmd.Cmd):
    def __init__(self, server):
        super(CmdShell, self).__init__()
        self.server = server
        
    def do_quit(self, arg):
        self.server.shutdown()
        return True

logging.basicConfig(level = logging.DEBUG)
logging.info("Smart Home Hookserver [Aquos Control]")

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

