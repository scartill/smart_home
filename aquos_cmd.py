import logging
import sys
from aquos import AquosControl

logging.basicConfig(level=logging.DEBUG)
logging.info("Sharp Aquos Command")

with AquosControl() as ac:
    ac.send_command(sys.argv[1], sys.argv[2])
