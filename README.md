# Nimses Adimate (Nimses Ad Automate)

[![GitHub issues](https://img.shields.io/github/issues/GiantTreeLP/nimses-adimate.svg)](https://github.com/GiantTreeLP/nimses-adimate/issues)
[![GitHub stars](https://img.shields.io/github/stars/GiantTreeLP/nimses-adimate.svg)](https://github.com/GiantTreeLP/nimses-adimate/stargazers)
[![PyPI](https://img.shields.io/pypi/v/nimses-adimate.svg)](https://pypi.org/project/nimses-adimate/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nimses-adimate.svg)
![PyPI - Status](https://img.shields.io/pypi/status/nimses-adimate.svg)


This script automatically clicks ads in the Nimses Android app.

Simply launch the `nimses.py` script and follow the instructions.
They will guide you through connecting your Android Smartphone to your PC.  
First it needs to be connected through USB to switch to networked mode and then use WiFi
for the rest of the process.

## Requirements

- An Android device, preferably with a modern version of Android
- USB Debugging enabled on that device

## Recommendations

This script and the Nimses app itself consume quite a bit of power, 
just keep your phone charging the whole time and don't worry about the power consumption.  

You should also enable "Stay awake" to make sure your device doesn't lock itself. 

## Dependencies

This script uses the following libraries:

- [`adbutils`](https://pypi.org/project/adbutils)
- [`opencv-python`](https://pypi.org/project/opencv-python/)
- [`numpy`](https://pypi.org/project/numpy/)

## Binary dependencies

This script requires the Android Debugging Bridge (ADB).
The Windows binaries are bundled with this repository. 
If you are using a different operating system, make sure the `adb` executable is in the executable path.

