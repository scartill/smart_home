import logging
import sys
from aquos import *

logging.basicConfig(level = logging.DEBUG, force = True)
logging.info("Sharp Aquos Command")

with AquosControl() as ac:
    ac.send_command(sys.argv[1], sys.argv[2])
