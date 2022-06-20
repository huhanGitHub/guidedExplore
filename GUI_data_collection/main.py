import csv
from dataclasses import dataclass
from functools import wraps

import definitions
from definitions import APK_DIR
from utils.util import *


def add_method(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func  # returning func means func can still be used normally

    return decorator


@dataclass
class ScreenCapture:
    apk_name: str
    activity_name: str
    directory: str


class Device(u2.Device):
    """
    Class for capture both phone and tablet UI data using only tablet device.
    Change density-independent pixels(dp)
    https://developer.android.com/training/multiscreen/screendensities
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.rotate("natural")
        self.font()
        self.to_tablet()

    def to_tablet(self):
        return self.res(1300, 800)

    def is_tablet(self):
        return self.info["displaySizeDpX"] == 1300

    def to_phone(self):
        return self.res(400, 900)

    def is_phone(self):
        return self.info["displaySizeDpX"] == 400

    def font(self, scale=1.00):
        out, code = self.shell(f"settings put system font_scale {scale}")
        print(f"{code}: seting font to {scale}")
        return self

    def res(self, w=1200, h=2000):
        """
        px = dp * (dpi / 160)
        """
        out, code = self.shell(f"wm size {w}dpx{h}dp")
        print(f"{code}: changing resolution to {w}dpx{h}dp")
        return self

    def rotate(self, dirt="natural"):
        """
        dirt=['left', 'right', 'natural', 'upsidedown']
        """
        self.set_orientation(dirt)
        self.shell("wm set-user-rotation free")
        return self

    def save(self, out_dir):
        # recording
        # TODO add resolution check
        s1 = s2 = None
        xml1 = self.dump_hierarchy(False, True)
        img1 = self.screenshot()
        if self.is_tablet():
            self.to_phone()
            s1, s2 = "tablet", "phone"
        else:
            self.to_tablet()
            s1, s2 = "phone", "tablet"
        time.sleep(1)  # wait for rerendering
        xml2 = self.dump_hierarchy(False, True)
        img2 = self.screenshot()

        # writing
        def getPath(filename, filetype):
            return os.path.join(out_dir, f"{filename}.{filetype}")

        if img1 is None or img2 is None:
            print("no images, save fail, return")
            return

        xml1Path = getPath(s1, "xml")
        img1Path = getPath(s1, "png")
        xml2Path = getPath(s2, "xml")
        img2Path = getPath(s2, "png")

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        with open(xml1Path, "w+", encoding="utf8") as f1, open(
            xml2Path, "w+", encoding="utf8"
        ) as f2:
            f1.write(xml1)
            img1.save(img1Path)
            f2.write(xml2)
            img2.save(img2Path)

        # saving metadata
        out_path = definitions.CSV_VM
        i = self.app_current()
        d = ScreenCapture(i["package"], i["activity"], out_dir)
        fieldnames = list(vars(d))
        if not os.path.exists(out_path):
            with open(out_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
        with open(out_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(vars(d))

    def install(self, apk_path):
        self.app_install(apk_path)
        apk_name = APK(apk_path).get_package()
        self.app_start(apk_name)

    def cur_info(d):
        isLauncher = False
        try:
            d_current = d.app_current()
        except OSError as e:
            print(e)
            return None, None, None
        d_package = d_current["package"]
        d_activity = d_current["activity"]
        if "android" in d_activity and "Launcher" in d_activity:
            isLauncher = True
        # NOTE: require names are in Android standard.
        d_activity = d_activity[d_activity.rindex(".") + 1 :]
        d_package = d_package[d_package.rindex(".") + 1 :]
        return d_activity, d_package, isLauncher


def main():
    # tablet = Device(definitions.TABLET_ID)
    tablet = Device(definitions.VM_ID)

    def install():
        apk_paths = sorted(os.listdir(definitions.APK_DIR))
        apk_paths = map(lambda x: os.path.join(APK_DIR, x), apk_paths)
        apk_paths = [f for f in apk_paths if os.path.isfile(f)]

        l = len(apk_paths)
        for i in list(enumerate(apk_paths + ["exit"])):
            print(i)
        i = int(input("Enter a index: "))
        if i == l:
            return
        else:
            tablet.install(apk_paths[i])

    def screenshots():
        t = str(int(time.time()))
        out_dir = os.path.join(definitions.OUT_DIR, t)
        tablet.save(out_dir)

    def cur():
        print(str(tablet.app_current()) + "\n")

    def nothing():
        pass

    d = {
        "refresh": nothing,
        "screenshot": screenshots,
        "install": install,
        "current": cur,
    }

    while True:
        cmds = list(d)
        for i in list(enumerate(cmds)):
            print(i)
        i = int(input("Enter a index: "))
        d[cmds[i]]()


if __name__ == "__main__":
    main()
