import logging
import os

from utils.device import Device

_log_format = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] [pid:%(process)d] %(message).100s'

logging.basicConfig(
    format=_log_format,
    datefmt='%H:%M:%S',
    level=logging.INFO
)


def _create(dir):
    if not os.path.exists(dir):
        logging.info(f"Creating directory: {dir}")
        os.mkdir(dir)
    return dir


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
APK_DIR = _create(os.path.join(ROOT_DIR, "apks"))

DATA_DIR = _create(os.path.join(ROOT_DIR, "data"))
DEEPLINKS_PATH = os.path.join(DATA_DIR, "deeplinks_params.json")
# DEEPLINKS_PATH = os.path.join(DATA_DIR, "deeplinks.json")
DECOMPILE_DIR = _create(os.path.join(DATA_DIR, "decompiled_apks"))
REPACKAGE_DIR = _create(os.path.join(DATA_DIR, "repackaged_apks"))
ATG_DIR = _create(os.path.join(DATA_DIR, "activity_atg"))
VISIT_RATE_DIR = _create(os.path.join(DATA_DIR, "visited_rate"))
OUT_DIR = _create(os.path.join(DATA_DIR, "outputs"))


# Android identifiers (serial number or ip address)
# get by $> adb devices
PHONE_ID = "LMK420TSUKR8PVTG7P"
TABLET_ID = "R52RA0C2MFF"
VM_ID = "192.168.57.101:5555"


# lazy initialize
_device = None


def _get_device():
    global _device
    if _device is None:
        _device = Device(VM_ID)
    return _device


device = _get_device()
