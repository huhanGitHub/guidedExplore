import logging
import os
import time
from datetime import datetime
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from itertools import chain

from functools import reduce
import definitions
from adbutils import AdbError
from dynamic_testing.activity_launcher import (
    launch_activity_by_deeplinks,
    launch_activity_by_deeplink,
)
from dynamic_testing.grantPermissonDetector import dialogSolver
from dynamic_testing.testing_path_planner import PathPlanner
from pyaxmlparser import APK
from uiautomator2.exceptions import GatewayError
from utils.device import Device
from utils.util import getActivityPackage
from utils.xml_helpers import clickable_bounds, find_google_login, click_if_find, type_if_find, is_same_activity

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[1;34m"
NC = "\033[0m"  # Clear Color


def desktop_notification():
    # NOTE: only works on linux
    os.system("notify-send -u critical -t 3000 error when collecting")


def left_bound(bounds):
    (x1, y1, x2, y2) = bounds
    return x1, y1
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    return x, y


def one_at_a_level(bs, nb):
    x, y = nb
    for (a, b) in bs:
        if (a == x or y == b):
            return bs
    return bs + [nb]


def click_clickables(d: Device, succeed_link):
    return
    xml = d.dump_hierarchy(compressed=True)
    root = ElementTree.fromstring(xml)
    bounds = clickable_bounds(root)
    # bounds = map(left_bound, clickable_bounds(root))

    # maxy = max(map(lambda b: b[1], bounds), default=-1)
    # bottoms = filter(lambda b: b[1] == maxy, bounds)
    # rest = filter(lambda b: b[1] != maxy, bounds)

    # bounds = chain(reduce(one_at_a_level, rest, []), bottoms)
    for (x1, y1, x2, y2) in bounds:
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        logging.info(f"click: {x},{y}")
        d.click(x, y)
        # TODO check if is changed
        try:
            d.hide_keyboard(root)
            if not is_same_activity(xml, d.dump_hierarchy(compressed=True), 0.9):
                d.collect_data()
                logging.info("collected a pair")
        except Exception as e:
            logging.error(f"{RED}fail to collect data{NC}, {type(e).__name__}: {e}")
        d.press("back")
        launch_activity_by_deeplink(*succeed_link)


def explore_cur_activity(d, path_planner, succeed_link, timeout=60):
    d_activity, d_package, isLauncher = getActivityPackage(d)
    logging.info(f"exploring {d_activity}")
    # collect data of current activity
    try:
        d.hide_keyboard()
        d.collect_data()
        logging.info(f"{GREEN}collected a pair{NC}")
        path_planner.set_visited(d_activity)
        if d.device_type():
            click_clickables(d, succeed_link)
    except Exception as e:
        logging.error(f"{RED}fail to collect data{NC}, {type(e).__name__}: {e}")
        import traceback
        logging.debug(traceback.format_exc())


def search_elements_from_XMLElement(source, target):
    root = ET.fromstring(source)
    for node in root.iter("node"):
        # if node.attrib["clickable"] == "false":
        #     continue
        node_text = node.attrib["text"].lower()
        if target.lower() in node_text:
            return node.attrib["resource-id"]
    # print('not found')
    # seach for unclickable if not found
    for node in root.iter("node"):
        if node.attrib["clickable"] == "false":
            node_text = node.attrib["text"].lower()
            if target.lower() in node_text:
                return node.attrib["resource-id"]
    return None


def search_input_from_XMLElement(source, target):
    root = ET.fromstring(source)
    for node in root.iter("node"):
        # print(node.attrib['text'])
        if node.attrib["class"] != "android.widget.EditText":
            if not (
                "Text" in node.attrib["class"]
                and node.attrib["focusable"] == "true"
                and node.attrib["clickable"] == "true"
            ):
                continue
        node_text = node.attrib["text"].lower()
        id_text = node.attrib["resource-id"].lower()
        if target.lower() in node_text or target.lower() in id_text:
            return node.attrib["resource-id"]
    return None


login_options = {
    "password": "Qsc,./136",
    "email": "guiautomation1@gmail.com",
    "username": "woodside",
    "activityName": "no"
}


def login_with_google(d, login_options):
    """
    the connected device need to login into a google account
    """
    logging.info("trying google login")
    try:
        xml = d.dump_hierarchy()
        pos = find_google_login(xml)
        if pos is None:
            return False
        else:
            d.click(*pos)
            print("clicked google")
            time.sleep(3)
            first_acc = "com.google.android.gms:id/account_display_name"
            d(resourceId=first_acc).click()
    except Exception as e:
        print("Failed to start {} because {}".format(login_options["activityName"], e))
        return False
    return True


def login_with_facebook(d, login_options):
    """
    need to disable google autologin
    """
    logging.info("trying facebook login")
    try:
        # check facebookLogin
        if click_if_find(d, {"text": "facebook"}):
            time.sleep(5)
        else:
            return False

        if type_if_find(d, {"text": "password"}, login_options["password"]) and \
           type_if_find(d, {"text": "email"}, login_options["email"]):
            d.press("enter")
            time.sleep(5)
        found = click_if_find(d, {"text": "continue", "class": "android.widget.Button"})
        if found:
            time.sleep(5)
        return found
    except Exception as e:
        logging.critical(f"something wrong, {type(e).__name__}: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return False
    return True


def try_login(d, login_options):
    try:
        if login_with_facebook(d, login_options):
            return True

        # if login_with_google(d, login_options):
        #     return True

        xml = d.dump_hierarchy()
        # check if need an extra move
        elementId = search_elements_from_XMLElement(xml, "already have an account")
        if elementId is None:
            elementId = search_elements_from_XMLElement(xml, "log in")
        if elementId is None:
            elementId = search_elements_from_XMLElement(xml, "sign in")
        if elementId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=elementId).click()

        #     try to input username and password
        xml = d.dump_hierarchy()
        usernameTextEditId = search_input_from_XMLElement(xml, "email")
        if usernameTextEditId is None:
            usernameTextEditId = search_input_from_XMLElement(xml, "username")
        if usernameTextEditId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=usernameTextEditId).set_text(login_options["username"])

        passwordTextEditId = search_input_from_XMLElement(xml, "password")
        if passwordTextEditId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=passwordTextEditId).set_text(login_options["password"])

        # click login button
        d.press("back")
        xml = d.dump_hierarchy()
        elementId = search_elements_from_XMLElement(xml, "log in")
        if elementId is None:
            elementId = search_elements_from_XMLElement(xml, "sign in")
        if elementId is not None:
            d.implicitly_wait(20.0)
            d(resourceId=elementId).click()
    except Exception as e:
        print("Failed to start {} because {}".format(login_options["activityName"], e))
        return False

    return True


def grant_all_permissions(d, apk):
    for permission in apk.permissions:
        d.shell(f"pm grant {apk.package} {permission}")


def unit_dynamic_testing(
    d: Device,
    apk: APK,
    atg_json,
    deeplinks_json,
    log_save_path,
    test_time=1200,
    reinstall=True,
):
    visited_rates = []
    pkg_name = apk.package
    apk_path = apk.filename
    deviceId = d._serial

    d.app_uninstall(pkg_name)
    d.app_install(apk_path)
    grant_all_permissions(d, apk)

    d.app_start(pkg_name)
    time.sleep(15)
    try_login(d, login_options)
    path_planner = PathPlanner(pkg_name, atg_json, deeplinks_json)
    unvisited = path_planner.get_unvisited_activity_deeplinks()
    # open launcher activity
    # TODO may faile BaseError
    dialogSolver(d)

    if unvisited is None:
        unvisited = []

    save_dir = os.path.join(definitions.OUT_DIR, pkg_name)
    if not os.path.exists(save_dir):
        logging.info(f"Creating directory: {save_dir}")
        os.mkdir(save_dir)

    visited_rates.append(path_planner.get_visited_rate())

    start_time = datetime.now()
    for (activity, deeplinks, actions, params) in unvisited:
        logging.info(f"{YELLOW}trying to open{NC} {activity}")
        try:
            status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
            path_planner.set_popped(activity)
            time.sleep(1)
            # check activity
            if not d.is_running(activity):
                print(d.current_activity())
                logging.error(f"{RED}fail to open target{NC}: {activity}")
                status = False

            if d.handle_syserr():
                logging.error(f"{RED}found system error prompt{NC}")
                status = False

            if status:
                path_planner.set_visited(activity)
                # key function here
                explore_cur_activity(d, path_planner, status, timeout=60)
            else:
                d.app_stop(pkg_name)
        # VM/device crash
        except AdbError as e:
            logging.critical(f"device is probably offline, {e}")
            desktop_notification()
            input("===watting for reset connection manually===")
        except RuntimeError as e:
            if "is offline" in str(e):
                logging.critical(f"device is probably offline, {e}")
                desktop_notification()
                input("===watting for reset connection manually===")
            else:
                raise e
        # android system crash
        except GatewayError as e:
            logging.critical(f"{e}, trying to restart")
            while True:
                try:
                    d = definitions.get_device()
                    break
                except GatewayError:
                    time.sleep(5)
        # others
        except Exception as e:
            logging.critical(f"something wrong, {type(e).__name__}: {e}")

            import traceback
            logging.debug(traceback.format_exc())
            logging.critical(f"skip {activity}, trying next activity")
            try:
                d.collect_data(definitions.ERROR_DIR)
            except Exception:
                logging.critical("unable to collect error data")

    delta = datetime.now() - start_time
    logging.info(f"visited rate:{path_planner.get_visited_rate()} in {delta}")
    path_planner.log_visited_rate(visited_rates, path=log_save_path)
    d.app_stop_all()
    d.app_uninstall(pkg_name)
    return True


if __name__ == "__main__":
# com.google.android.gms:id/account_display_name
    # deviceId = '192.168.57.105'
    deviceId = "192.168.57.101:5555"
    # deviceId = 'cb8c90f4'
    # deviceId = 'VEG0220B17010232'
    d = Device(definitions.EM_ID)
    # login_with_facebook(d, login_options)
    try_login(d, login_options)
    # d.app_start("com.alltrails.alltrails")
    # login_with_google(d, login_options)
    # d.collect_data(definitions.DATA_DIR)
    # d.app_start("com.twitter.android")
    # print(d.current_activity())
    # login_with_facebook(d, login_options)
    # print(find_google_login(d.dump_hierarchy(compressed=True)))
    # d.xpath("//*[contains(@text, 'Google')]").click()

    # name = "Lightroom"
    # apk_path = os.path.join(definitions.REPACKAGE_DIR, f"{name}.apk")
    # atg_json = os.path.join(definitions.ATG_DIR, f"{name}.json")
    # deeplinks_json = definitions.DEEPLINKS_PATH
    # log = os.path.join(definitions.VISIT_RATE_DIR, f"{name}.txt")
    # unit_dynamic_testing(
    #     Device(deviceId), APK(apk_path), atg_json, deeplinks_json, log, reinstall=False
    # )
