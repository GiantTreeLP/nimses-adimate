import logging
import os
import sys
from pathlib import Path

from .android.adb import switch_to_tcpip
from .nimses import main

if __name__ == '__main__':
    """
    Launches nimses-adimate.
    This launch script appends the platform-tools directory to the end of the PATH variable in order for certain 
    operating systems to find the `adb` executable.
    Then it switches ADB to "tcpip" mode and launches the actual main code.
    """
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    os.environ["PATH"] += os.pathsep + str(Path(__file__).parent) + os.sep + "platform-tools"

    device = switch_to_tcpip()
    main(device)
