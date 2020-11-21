import logging
import socket
import os
import time

RVC_BUFFER_SIZE = 1024
RETRIES = 3
RETRY_TIMEOUT = 3


class AquosControl(object):
    def __init__(self):
        self.sock = None

    def __enter__(self):
        retry = 1
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip = os.getenv('AQUOS_TCP_IP')
                port = int(os.getenv('AQUOS_TCP_PORT'))
                self.sock.connect((ip, port))
            except Exception as exc:
                logging.warning(
                    "Connect exception {} (retry {})".format(exc, retry))
                self.sock.close()

                if retry < RETRIES:
                    retry += 1
                    time.sleep(RETRY_TIMEOUT)
                    continue
                else:
                    raise
            else:
                break

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
    @staticmethod
    def power_off():
        with AquosControl() as ac:
            ac.send_bool("RSPW", True)
            ac.send_bool("POWR", False)

    @staticmethod
    def power_on():
        with AquosControl() as ac:
            ac.send_bool("RSPW", True)
            ac.send_bool("POWR", True)

    @staticmethod
    def channel(channel):
        with AquosControl() as ac:
            ac.send_command("DTVD", channel)

    @staticmethod
    def hdmi(number):
        with AquosControl() as ac:
            ac.send_command("IAVD", number)
