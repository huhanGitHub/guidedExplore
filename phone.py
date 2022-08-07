import logging
import os
import shutil
import threading
import time
from datetime import datetime
from functools import reduce
from itertools import chain
from xml.etree import ElementTree
from xml.etree import ElementTree as ET

from adbutils import AdbError
from pyaxmlparser import APK
from uiautomator2.exceptions import GatewayError

import definitions
from decompile_apk import unit_decompile
from definitions import APK_DIR, DATA_DIR, DECOMPILE_DIR, REPACKAGE_DIR
from dynamic_testing.activity_launcher import (
    launch_activity_by_deeplink,
    launch_activity_by_deeplinks,
)
from dynamic_testing.grantPermissonDetector import dialogSolver
from dynamic_testing.testing_path_planner import PathPlanner
from run_preprocess import unit_run_preprocess_one
from utils.device import Device
from utils.path import basename_no_ext
from utils.util import getActivityPackage, installApk
from utils.xml_helpers import (
    click_if_find,
    clickable_bounds,
    find_google_login,
    is_same_activity,
    type_if_find,
)

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[1;34m"
NC = "\033[0m"  # Clear Color


def collect_data(device, save_dir=None):
    cur_pkg = device.current_package()
    if save_dir is None:
        save_dir = os.path.join(definitions.DATA_DIR, "compare", "click", cur_pkg)
        if not os.path.exists(save_dir):
            logging.info(f"Creating directory: {save_dir}")
            os.mkdir(save_dir)

    p_act, p_xml, p_img = device.collect_cur_activity()

    if p_img is None:
        logging.error("none img, save fail, return")
        return False

    t = int(time.time())

    def get_path(device, filetype):
        act = p_act if device == "phone" else t_act
        return os.path.join(save_dir, f"{t}_{device}_{act}.{filetype}")

    xml2Path = get_path("phone", "xml")
    img2Path = get_path("phone", "png")
    with open(xml2Path, "a", encoding="utf8") as f2:
        f2.write(p_xml)
        p_img.save(img2Path)
    return True


def desktop_notification():
    # NOTE: only works on linux
    os.system("notify-send -u critical -t 3000 error when collecting")


def explore_cur_activity(d, path_planner, succeed_link, timeout=60):
    d_activity, d_package, isLauncher = getActivityPackage(d)
    logging.info(f"exploring {d_activity}")
    # collect data of current activity
    try:
        d.hide_keyboard()
        collect_data(d)
        logging.info(f"{GREEN}collected{NC}")
        path_planner.set_visited(d_activity)
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
    "activityName": "no",
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

        if type_if_find(
            d, {"text": "password"}, login_options["password"]
        ) and type_if_find(d, {"text": "email"}, login_options["email"]):
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

        if login_with_google(d, login_options):
            return True

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
    pkg_name = apk.package
    apk_path = apk.filename
    deviceId = d._serial

    d.app_uninstall(pkg_name)
    d.app_install(apk_path)
    grant_all_permissions(d, apk)

    d.app_start(pkg_name)
    time.sleep(15)

    dialogSolver(d)
    try_login(d, login_options)
    path_planner = PathPlanner(pkg_name, atg_json, deeplinks_json)
    unvisited = path_planner.get_unvisited_activity_deeplinks()
    unvisited = [] if unvisited is None else unvisited

    save_dir = os.path.join(definitions.OUT_DIR, pkg_name)
    if not os.path.exists(save_dir):
        logging.info(f"Creating directory: {save_dir}")
        os.mkdir(save_dir)

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
                    time.sleep(10)
        # others
        except Exception as e:
            logging.critical(f"something wrong, {type(e).__name__}: {e}")

            import traceback

            logging.debug(traceback.format_exc())
            logging.critical(f"skip {activity}, trying next activity")

    delta = datetime.now() - start_time
    logging.info(f"visited rate:{path_planner.get_visited_rate()} in {delta}")
    d.app_stop_all()
    d.app_uninstall(pkg_name)
    return True


def explore(device, apk):
    """
    :param apk_path: recompiled apk path
    """
    name = apk.package
    logging.info(f"exploring {name}")

    atg_json = os.path.join(definitions.ATG_DIR, f"{name}.json")
    deeplinks_json = os.path.join(definitions.DEEPLINKS_DIR, f"{name}.json")
    log_file = os.path.join(definitions.VISIT_RATE_DIR, f"{name}.txt")

    if not is_preprocessed(name):
        raise RuntimeError("failed to to preprocess or didn't preprocess")

    unit_dynamic_testing(
        device,
        apk,
        atg_json,
        deeplinks_json,
        log_file,
        reinstall=True,
    )


def log_failure(pkg):
    with open(definitions.FAIL_LOG_PATH, "a") as f:
        f.write(pkg)
        f.write("\n")


def unexplored_apks():
    explored_apps = [
        f.name
        for f in os.scandir(os.path.join(definitions.OUT_DIR, "deer"))
        if f.is_dir()
    ]
    failed_apps = [f for f in open(definitions.FAIL_LOG_PATH).read().splitlines()]
    ignored_apps = set(explored_apps).union(set(failed_apps))
    apks = [
        f.path
        for f in os.scandir(definitions.APK_DIR)
        if f.name.endswith(".apk") and f.name.removesuffix(".apk") not in ignored_apps
    ]
    return apks


def preprocess(apk_path):
    pkg_name = APK(apk_path).package
    decom_path = os.path.join(DECOMPILE_DIR, pkg_name)
    deeplinks_path = os.path.join(definitions.DEEPLINKS_DIR, f"{pkg_name}.json")

    if os.path.exists(decom_path):
        shutil.rmtree(decom_path)
    os.mkdir(decom_path)

    unit_decompile(apk_path, decom_path)

    repackaged_path = unit_run_preprocess_one(decom_path, REPACKAGE_DIR, deeplinks_path)
    return repackaged_path


def run(device, apk=None):
    """
    explore one apk or apks under `definitions.APK_DIR`
    example: apk=os.path.join(definitions.APK_DIR, "com.duolingo.apk")
    """
    # TODO check os.system commands if multi connected devices
    if apk is None:
        apks = unexplored_apks()
    else:
        apks = [apk]
    for apk_path in apks:
        try:
            apk = APK(apk_path)
            name = apk.package
            if not is_preprocessed(name):
                repack_path = preprocess(apk_path)
            else:
                repack_path = os.path.join(definitions.REPACKAGE_DIR, f"{name}.apk")

            ans = explore(device, apk)
            if ans is False:
                log_failure(basename_no_ext(apk_path))
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt, exiting")
            exit(0)
        except RuntimeError as e:
            if "is offline" in str(e):
                logging.critical(f"device is probably offline, {e}")
                input("===watting for reset connection manually===")
        except Exception as e:
            logging.critical(
                f"error when processing {basename_no_ext(apk_path)}, {type(e).__name__}:{e}"
            )
            import traceback

            logging.debug(traceback.format_exc())
            log_failure(basename_no_ext(apk_path))
        finally:
            device.app_stop_all()
            device.app_uninstall(name)


def run(device, apk=None):
    """
    explore one apk or apks under `definitions.APK_DIR`
    example: apk=os.path.join(definitions.APK_DIR, "com.duolingo.apk")
    """
    # TODO check os.system commands if multi connected devices
    if apk is None:
        apks = unexplored_apks()
    else:
        apks = [apk]
    for apk_path in apks:
        try:
            apk = APK(apk_path)
            name = apk.package
            if not is_preprocessed(name):
                repack_path = preprocess(apk_path)
            else:
                repack_path = os.path.join(definitions.REPACKAGE_DIR, f"{name}.apk")

            ans = explore(device, apk)
            if ans is False:
                log_failure(basename_no_ext(apk_path))
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt, exiting")
            exit(0)
        except RuntimeError as e:
            if "is offline" in str(e):
                logging.critical(f"device is probably offline, {e}")
                input("===watting for reset connection manually===")
        except Exception as e:
            logging.critical(
                f"error when processing {basename_no_ext(apk_path)}, {type(e).__name__}:{e}"
            )
            import traceback

            logging.debug(traceback.format_exc())
            log_failure(basename_no_ext(apk_path))
        finally:
            device.app_stop_all()
            device.app_uninstall(name)


def main():
    apk = os.path.join(definitions.APK_DIR, "com.duckduckgo.mobile.android.apk")
    # em = Device(definitions.EM_ID, True, False)
    apk = None
    apk = os.path.join(
        "~",
        "Download",
        "Amazon Prime Video by Amazon Mobile LLC - com.amazon.avod.thirdpartyclient.apk",
    )
    em = Device(definitions.VM_ID, False, True)
    em.to_phone()
    run(em, apk)


if __name__ == "__main__":
    main()
