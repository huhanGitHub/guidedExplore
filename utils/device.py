import logging
import os
import time
from xml.etree import ElementTree

import uiautomator2 as u2

import definitions

from .xml_helpers import exits_keyboard, exits_syserr

RES_WAIT = 2  # second(s), time to wait when changing resolution.


class ResolutionError(Exception):
    pass


class Device(u2.Device):
    """
    Class for capture both phone and tablet UI data using only tablet device.
    Note that operation delay are applied during initialization.

    Change density-independent pixels(dp)
    https://developer.android.com/training/multiscreen/screendensities
    """

    def __init__(self, id, flip_res=True, tablet_natural=False):
        # TODO disable animations
        super().__init__(id)
        super().settings["operation_delay"] = (0, 10)
        super().settings["operation_delay_methods"] = ["click", "swipe", "press"]
        self.font()
        #  turn off the automatic rotation
        self.shell("settings put system accelerometer_rotation 1")
        self._flip_res = flip_res
        self._tablet_natural = tablet_natural
        # self.init_landscape()
        self.to_default()

    def init_landscape(self):
        self.shell("wm size reset")
        self.shell("settings put system user_rotation 1")
        time.sleep(RES_WAIT)
        x = self.info["displayWidth"]
        y = self.info["displayHeight"]
        print(self.info)
        if x < y and self.info["naturalOrientation"]:
            self.shell("settings put system user_rotation 1")
            self._flip_res = False
        return self

    TABLET_W = 1300
    TABLET_H = 800

    def to_tablet(self):
        logging.debug("changing to tablet resolution")
        return self.res(Device.TABLET_W, Device.TABLET_H)

    def is_tablet(self):
        return (
            self.info["displaySizeDpX"] == Device.TABLET_W
            and self.info["displaySizeDpY"] == Device.TABLET_H
        )

    PHONE_W = 400
    PHONE_H = 900

    def to_phone(self):
        logging.debug("changing to phone resolution")
        return self.res(Device.PHONE_W, Device.PHONE_H)

    def is_phone(self):
        return (
            self.info["displaySizeDpX"] == Device.PHONE_W
            and self.info["displaySizeDpY"] == Device.PHONE_H
        )

    def to_default(self):
        self.to_tablet()
        if self._tablet_natural:
            self.shell("settings put system user_rotation 0")
        else:
            self.shell("settings put system user_rotation 1")
        return self

    def device_type(self):
        if self.is_tablet():
            return "tablet"
        elif self.is_phone():
            return "phone"
        else:
            raise ResolutionError(
                f"Not at a defined resolution or wrong orientation,\
at {self.info['displaySizeDpX']}x{self.info['displaySizeDpY']}"
            )

    def change_device_type(self):
        if self.is_tablet():
            self.to_phone()
        elif self.is_phone():
            self.to_tablet()
        else:
            self.to_tablet()
        return self

    def font(self, scale=1.00):
        out, code = self.shell(f"settings put system font_scale {scale}")
        return self

    def res(self, w=None, h=None):
        """
        px = dp * (dpi / 160)
        """
        if self._flip_res:
            w, h = h, w
        if w is None or h is None:
            out, code = self.shell("wm size reset")
        else:
            out, code = self.shell(f"wm size {w}dpx{h}dp")
        time.sleep(RES_WAIT)
        return self

    def current_activity(self, fullname=False):
        """
        fallname = package name + activity fullname
        """
        app = self.app_current()

        activity = app["activity"]
        if fullname:
            return app["package"] + activity
        else:
            return activity[activity.rindex(".") + 1 :]

    def collect_cur_activity(self, hide_keyboard=True):
        activity = self.current_activity()
        if hide_keyboard:
            self.hide_keyboard()
        xml = self.dump_hierarchy(compressed=True)
        img = self.screenshot()
        return activity, xml, img

    def collect_pair(self):
        """
        return: tablet data, phone data
        """
        pair = {}
        self.change_device_type()
        pair[self.device_type()] = self.collect_cur_activity()
        self.to_default()
        pair[self.device_type()] = self.collect_cur_activity()
        return *pair["tablet"], *pair["phone"]

    def app_start_wait(self, package):
        self.app_start(package, wait=True)
        activity = self.app_info(package)["mainActivity"]
        activity = f".{activity}" if activity.find(".") == -1 else activity
        self.wait_activity(activity)
        return self

    def current_package(self):
        return self.app_current()["package"]

    def collect_data(self, save_dir=None):
        """
        Collect both tablet and phone data using tablet device.

        This method will automatictly save to subfolder of `definitions.OUT_DIR`
        if not pass argument to `save_dir`.
        """
        if save_dir is None:
            save_dir = os.path.join(definitions.OUT_DIR, self.current_package())
            if not os.path.exists(save_dir):
                logging.info(f"Creating directory: {save_dir}")
                os.mkdir(save_dir)
        t_act, t_xml, t_img, p_act, p_xml, p_img = self.collect_pair()

        if p_img is None or t_img is None:
            logging.error("none img, save fail, return")
            return False

        t = int(time.time())

        def get_path(device, filetype):
            act = p_act if device == "phone" else t_act
            return os.path.join(save_dir, f"{t}_{device}_{act}.{filetype}")

        xml1Path = get_path("tablet", "xml")
        img1Path = get_path("tablet", "png")
        xml2Path = get_path("phone", "xml")
        img2Path = get_path("phone", "png")
        with open(xml1Path, "a", encoding="utf8") as f1, open(
            xml2Path, "a", encoding="utf8"
        ) as f2:
            f1.write(t_xml)
            f2.write(p_xml)
            t_img.save(img1Path)
            p_img.save(img2Path)
        return True

    def get_view_root(self):
        xml = self.dump_hierarchy(compressed=True)
        root = ElementTree.fromstring(xml)
        return root

    def hide_keyboard(self, root=None):
        if root is None:
            root = self.get_view_root()

        exits = exits_keyboard(root)
        if exits:
            logging.info("found keyboard")
            self.press("back")
        return exits

    def handle_syserr(self, root=None):
        """
        check system prompt with title like '...keeps stopping'
        """
        if root is None:
            root = self.get_view_root()
        exits = exits_syserr(root)
        if exits:
            self.press("home")
        return exits

    def is_running(self, activity: str):
        cur_act = self.current_activity()
        ans = activity.endswith(cur_act)
        return ans


if __name__ == "__main__":
    d = Device(definitions.VM_ID)
