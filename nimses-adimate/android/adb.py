import logging
import subprocess
from pathlib import Path
from typing import List

from adbutils import adb_path, adb

logger = logging.getLogger(__name__)


def execute_adb(args: List[str], **kwargs):
    cmdline = [adb_path()]
    cmdline.extend(args)
    cmdline = subprocess.list2cmdline(cmdline)
    return subprocess.check_output(cmdline,
                                   cwd=Path(adb_path()).parent,
                                   stderr=subprocess.STDOUT,
                                   encoding="utf-8",
                                   **kwargs)


def switch_to_tcpip(port: int = 5555):
    logger.info("Checking for connected devices")
    try:
        output = execute_adb(["wait-for-local-device"], timeout=1)
        logger.info("[ADB] %s", output)
        network_device = next(filter(lambda d: ":" in d.serial, adb.device_list()))
        if network_device is not None:
            logger.info("Found connected device: %s", network_device)
            return network_device
    except subprocess.TimeoutExpired:
        logger.warning("No networked device found.")
        pass

    logger.info("Switching to tcpip for USB connected device")
    logger.info("Waiting for device")
    output = execute_adb(["wait-for-usb-device"])
    logger.info("[ADB] %s", output)
    ip = adb.device().wlan_ip()
    logger.info(f"Trying to connect to {ip}:{port}")
    output = execute_adb(["-d", "tcpip", f"{port}"])
    logger.info("[ADB] %s", output)
    try:
        output = execute_adb(["disconnect", f"{ip}:{port}"])
    except subprocess.CalledProcessError as e:
        logger.warning("[ADB] %s", e)
    logger.info("[ADB] %s", output)
    output = adb.connect(f"{ip}:{port}")
    logger.info("[ADB] %s", output)
    output = execute_adb(["wait-for-local-device"])
    logger.info("[ADB] %s", output)
    logger.info("Please remove the USB device")
    return adb.device(f"{ip}:{port}")
