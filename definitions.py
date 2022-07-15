import logging
import os

from utils.device import Device

BLUE = "\033[1;34m"
NC = "\033[0m"  # No Color

_log_format = f"{BLUE}[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]{NC} %(message)s"

logging.basicConfig(format=_log_format, datefmt="%H:%M:%S", level=logging.INFO)


def _create(dir):
    if not os.path.exists(dir):
        logging.info(f"Creating directory: {dir}")
        os.mkdir(dir)
    return dir


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
APK_DIR = _create(os.path.join(ROOT_DIR, "apks"))

DATA_DIR = _create(os.path.join(ROOT_DIR, "data"))
DEEPLINKS_PATH = os.path.join(DATA_DIR, "deeplinks_params.json")
FAIL_LOG_PATH = os.path.join(DATA_DIR, "failed_package.log")

DEEPLINKS_DIR = _create(os.path.join(DATA_DIR, "deeplinks"))
# DEEPLINKS_PATH = os.path.join(DATA_DIR, "deeplinks.json")
DECOMPILE_DIR = _create(os.path.join(DATA_DIR, "decompiled_apks"))
REPACKAGE_DIR = _create(os.path.join(DATA_DIR, "repackaged_apks"))
ATG_DIR = _create(os.path.join(DATA_DIR, "activity_atg"))
VISIT_RATE_DIR = _create(os.path.join(DATA_DIR, "visited_rate"))
OUT_DIR = _create(os.path.join(DATA_DIR, "outputs"))
ERROR_DIR = _create(os.path.join(DATA_DIR, "error"))

# Android identifiers (serial number or ip address)
# get by $> adb devices
PHONE_ID = "LMK420TSUKR8PVTG7P"
TABLET_ID = "R52RA0C2MFF"
VM_ID = "192.168.57.101:5555"


# lazy initialize
_device = None


def get_device():
    global _device
    if _device is None:
        _device = Device(VM_ID)
        _device._logger.level = logging.INFO
    return _device
