import logging
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from time import time, sleep, strftime, localtime
from typing import Tuple

import cv2
import numpy as np
from adbutils import adb, AdbDevice

from .android.async_helper import log_error
from .android.screencap import screencap_png

# CONSTANTS
PLAYSTORE_PACKAGE = "com.android.vending"
NIMSES_PACKAGE = "com.nimses"
NIMSES_MAIN_ACTIVITY = "com.nimses.navigation.presentation.view.screens.main.MainActivity"
NIMSES_AD_ACTIVITIES = (
    "com.adcolony.sdk.AdColonyInterstitialActivity",
    "com.unity3d.ads.adunit.AdUnitActivity",
    "com.unity3d.services.ads.adunit.AdUnitActivity",
    "com.ironsource.sdk.controller.ControllerActivity"
)

TEMPLATE_AD_IMAGE = cv2.imread(str(Path(__file__).parent) + "/templates/ads_inline_fhd_de.png", cv2.IMREAD_GRAYSCALE)

logger = logging.getLogger("NAD")


def screen_shot_android(device: AdbDevice) -> np.ndarray:
    """
    Takes a screen shot of the given Android device.
    This method just exists to easily change the implementation of the screen shot mechanism.

    :param device: the device to take a screen shot from
    :return: the screen shot in a raw `ndarray`
    """
    return screencap_png(device)


def find_image(image: np.ndarray, search: np.ndarray, threshold=0.05, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
    """
    Finds an image inside another image with a maximum threshold and additional arguments.
    Uses `cv2.matchTemplate` with the `cv2.TN_SQDIFF_NORDME` method.

    :param image: the source image to search in; converted to grayscale for opencv.
    :param search: the image to search for in the source image.
    :param threshold: the maximum threshold for the source (default: 0.05)
    :param kwargs: additional arguments to `cv2.matchTemplate`
    :return: two `ndarray`s, one with the matches and one with the entire result image (grayscale, the darker the pixel,
    the more closely it match es the search image)
    """
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray, search, cv2.TM_SQDIFF_NORMED, **kwargs)
    return np.where(res <= threshold), res


def find_inline_ads(image: np.ndarray) -> Tuple[Tuple[int, int], np.ndarray]:
    """
    Finds and marks Nimses ads in a given image.
    Uses the `TEMPLATE_AD_IMAGE`.

    :param image: the image (screen shot usually) to search for ads in.
    :return: A tuple with the location as a tuple of x and y and the image that was searched in
    """
    pt = None
    try:
        loc, _ = find_image(image, TEMPLATE_AD_IMAGE)

        # Find the first (not the best) location
        pt = next(zip(*loc[::-1]), False)
        if pt:
            # Draw circle in the center of the match
            pt = (pt[0] + TEMPLATE_AD_IMAGE.shape[1] // 2, pt[1] + TEMPLATE_AD_IMAGE.shape[0] // 2)
            cv2.circle(image, pt, 16, (0, 0, 255, 255), 16)
    except Exception as e:
        print(e)

    # show_image(image)
    return pt, image


def handle_new_ad(ad: Tuple[Tuple[int, int], np.ndarray], device: AdbDevice, state: dict):
    """
    Handles a newly identified ad, whether or not there actually is one.
    This method also makes sure, that ads are closed again.
    Some ads open the Play Store, so this method also moves back to Nimses.

    :param ad: a tuple with the ad location (optional) and the screen shot.
    :param device: the Android device that should be controlled
    :param state: the global state of this application
    """

    def close_ad():
        """
        Closes the currently open ad (really just switches to the main activity)
        """
        if not state["ad_closed"] and state["ad_time"] < time():
            device.app_start(NIMSES_PACKAGE, NIMSES_MAIN_ACTIVITY)
            state["ad_closed"] = True
            logger.info("Closed ad")

    pt, image = ad
    app = device.current_app()
    logger.info("Current app %s", app)
    logger.info("Ad open? %s", not state["ad_closed"])

    if np.array_equal(image, state["last_image"]) \
            or state["last_ad"] > 10:
        output = device.shell(["am", "force-stop", NIMSES_PACKAGE])
        logger.info(f"[ADB] {output}")
        device.app_start(NIMSES_PACKAGE, NIMSES_MAIN_ACTIVITY)
        state["last_ad"] = 0
        state["ad_closed"] = True
        logger.info("Restarted Nimses")
    elif app["package"] == NIMSES_PACKAGE:
        if app["activity"] == NIMSES_MAIN_ACTIVITY:
            # Ad found, click it
            if pt:
                device.click(pt[0], pt[1])
                state["last_ad"] = 0
                state["ad_closed"] = True
                logger.info("Clicked %d, %d", pt[0], pt[1])
            # No ad, scroll along
            else:
                state["last_ad"] += 1
                w, h = device.window_size()
                sx = w // 2
                sy = h // 4 * 3
                dx = w // 2
                dy = h // 4 * 1
                device.swipe(sx, sy, dx, dy, 1.0)
        elif app["activity"] in NIMSES_AD_ACTIVITIES:
            if state["ad_closed"]:
                state["ad_time"] = time() + 35
                state["ad_closed"] = False
                logger.info("Close ad at: %s", strftime("%H:%M:%S", localtime(state["ad_time"])))
            else:
                close_ad()
    elif app["package"] == PLAYSTORE_PACKAGE:
        device.app_start(NIMSES_PACKAGE, NIMSES_MAIN_ACTIVITY)
        logger.info("Closed Play Store")
    else:
        device.app_start(NIMSES_PACKAGE, NIMSES_MAIN_ACTIVITY)


def main(device: AdbDevice = None):
    """
    Initializes the global state, sets up a ThreadPoolExecutor and launches the Nimses app.

    :param device: the device to control, if `None`, chooses the first and only device
    """
    executor = ThreadPoolExecutor(3)
    state = {
        "device": device if device is not None else adb.device(),  # The Android device to control
        "executor": executor,  # The executor where the magic happens
        "last_image": None,  # The last image
        "last_ad": 0,  # The amount of updates since the last ad
        "ad_closed": True,  # Whether the last ad has been closed
        "ad_time": 0  # When to close the app (in the future)
    }

    device.app_start(NIMSES_PACKAGE, NIMSES_MAIN_ACTIVITY)

    # Prepare future variable
    future = Future()
    future.set_result(None)
    while True:
        if future.done():
            future = executor.submit(
                lambda: log_error(
                    lambda: handle_new_ad(find_inline_ads(screen_shot_android(device)), device, state)))
        sleep(0.1)
