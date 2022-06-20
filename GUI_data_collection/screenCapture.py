import csv
import os
import time
from dataclasses import dataclass

import definitions
import uiautomator2 as u2
from utils.util import (connectionAdaptor, getActivityPackage, safeScreenshot,
                        save_screen_data)


@dataclass
class ScreenCapture:
    apk_name: str
    activity_name: str
    directory: str
    time: int

    def from_row(row, header):
        d = dict(zip(header, row))
        return ScreenCapture(d['apk_name'], d['activity_name'], d[ 'directory' ], d[ 'time' ])


def append_to_csv(d):
    fieldnames = list(vars(d))
    if not os.path.exists(definitions.CSV_PATH):
        with open(definitions.CSV_PATH, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    with open(definitions.CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(vars(d))


def save_screen_data(out_dir, xml1, xml2, img1, img2, activity_name, package_name):
    if img1 is None or img2 is None:
        print("none img, save fail, return")
        return

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    def getPath(devicetype, filetype):
        return os.path.join(out_dir, f"{devicetype}.{filetype}")

    xml1Path = getPath("phone", "xml")
    img1Path = getPath("phone", "png")
    xml2Path = getPath("tablet", "xml")
    img2Path = getPath("tablet", "png")

    with open(xml1Path, "w+", encoding="utf8") as f1, open(
        xml2Path, "w+", encoding="utf8"
    ) as f2:
        f1.write(xml1)
        f2.write(xml2)
        img1.save(img1Path)
        img2.save(img2Path)


def capture_ui_data(
    phoneDevice=definitions.PHONE_ID,
    tabletDevice=definitions.TABLET_ID,
):
    t = str(int(time.time()))
    out_dir = os.path.join(definitions.OUT_DIR, t)

    d1, d2, status = connectionAdaptor(phoneDevice, tabletDevice)
    while not status:
        d1, d2, status = connectionAdaptor(phoneDevice, tabletDevice)

    d1_activity, d1_package, isLauncher = getActivityPackage(d1)
    # d2_activity, d2_package, d2_launcher = getActivityPackage(d2)

    xml1 = d1.dump_hierarchy(compressed=True)
    xml2 = d2.dump_hierarchy(compressed=True)
    img1 = safeScreenshot(d1)
    img2 = safeScreenshot(d2)

    save_screen_data(out_dir, xml1, xml2, img1, img2, d1_activity, d1_package)
    append_to_csv(ScreenCapture(d1_package, d1_activity, out_dir, t))


def append_to_csv_tablet(d):
    out_path = definitions.TABLET_CSV_PATH
    fieldnames = list(vars(d))
    if not os.path.exists(out_path):
        with open(out_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    with open(out_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(vars(d))

def save_screen_data_tablet(out_dir, xml1, xml2, img1, img2, activity_name, package_name):
    if img1 is None or img2 is None:
        print("none img, save fail, return")
        return

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    def getPath(filename, filetype):
        return os.path.join(out_dir, f"{filename}.{filetype}")

    xml1Path = getPath("tablet_hor", "xml")
    img1Path = getPath("tablet_hor", "png")
    xml2Path = getPath("tablet_ver", "xml")
    img2Path = getPath("tablet_ver", "png")

    with open(xml1Path, "w+", encoding="utf8") as f1, open(
        xml2Path, "w+", encoding="utf8"
    ) as f2:
        f1.write(xml1)
        f2.write(xml2)
        img1.save(img1Path)
        img2.save(img2Path)

def capture_ui_data_tablet(tabletDevice=definitions.TABLET_ID):
    t = str(int(time.time()))
    out_dir = os.path.join(definitions.OUT_DIR, t)

    d1 = u2.connect(tabletDevice)

    d1_activity, d1_package, isLauncher = getActivityPackage(d1)

    d1.set_orientation('r')
    time.sleep(1) #wait for rotation
    xml1 = self.dump_hierarchy(compressed=True)
    img1 = self.screenshot()

    # rotate and record
    d1.set_orientation('n')
    time.sleep(1) #wait for rotation
    xml2 = self.dump_hierarchy(compressed=True)
    img2 = self.screenshot()

    save_screen_data_tablet(out_dir, xml1, xml2, img1, img2, d1_activity, d1_package)
    append_to_csv_tablet(ScreenCapture(d1_package, d1_activity, out_dir, t))


if __name__ == "__main__":
    # capture_ui_data()
    capture_ui_data_tablet()
