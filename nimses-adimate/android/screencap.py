import logging
import socket
from concurrent.futures import Executor
from time import time

import cv2
import numpy as np
from adbutils import AdbDevice

from .raw_socket import send_raw

logger = logging.getLogger(__name__)


def screencap_raw(device: AdbDevice):
    start = time()
    buffer = send_raw(device, "framebuffer:", 20 * 1024 * 1024)
    logger.debug("Recv RAW took %f seconds" % (time() - start))

    # Unpack the header
    version, bpp, colorspace, size, width, height, \
    red_offset, red_length, \
    blue_offset, blue_length, \
    green_offset, green_length, \
    alpha_offset, alpha_length = np.frombuffer(buffer, "uint32", 14)

    return cv2.cvtColor(np.reshape(np.frombuffer(buffer[14 * 4:], "uint8"), (height, width, 4)), cv2.COLOR_RGB2BGR)


def screencap_png(device: AdbDevice) -> np.ndarray:
    start = time()
    buffer = send_raw(device, "exec:screencap -p", 1024 * 1024)
    logger.debug("Recv PNG took %f seconds" % (time() - start))

    return cv2.imdecode(np.frombuffer(buffer, "uint8"), cv2.IMREAD_UNCHANGED)


def screencap_h264(device: AdbDevice, executor: Executor):
    start = time()
    device.push("../scrcpy-win64/scrcpy-server.jar", "/data/local/tmp/scrcpy-server.jar")
    print("Pushed server component")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = device.adb_output("reverse", "tcp:5556", "localabstract:scrcpy")
    print("[ADB]", port)
    # sock.bind(("127.0.0.1", 5556))
    # sock.listen()

    executor.submit(lambda: print("[SCRCPY]", device.shell("CLASSPATH=/data/local/tmp/scrcpy-server.jar "
                                                           "app_process / com.genymobile.scrcpy.Server 0 8000000 "
                                                           "false - false true")))
    print("Executed scrcpy")

    print("Waiting for connection")
    # conn, info = sock.accept()
    # print(info)
    # print(conn.recv(1))
    # print(conn.recv(64))
    # print(conn.recv(2))
    # print(conn.recv(2))
    # print("Closing transmission")
    # device.shell("\x03")
    # conn.close()
    # sock.close()
    print("Recv h264 took %f seconds" % (time() - start))
