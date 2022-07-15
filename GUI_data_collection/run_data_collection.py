import logging
import os
import time
from datetime import datetime

import definitions
from adbutils import AdbError
from dynamic_testing.activity_launcher import launch_activity_by_deeplinks
from dynamic_testing.grantPermissonDetector import dialogSolver
from dynamic_testing.hierachySolver import (GUI_state_change,
                                            click_points_Solver)
from dynamic_testing.testing_path_planner import PathPlanner
from pyaxmlparser import APK
from uiautomator2.exceptions import GatewayError
from utils.device import Device
from utils.util import getActivityPackage
from utils.xml_helpers import clickable_bounds

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[1;34m"
NC = "\033[0m"  # No Color


def desktop_notification():
    # NOTE: only works on linux
    os.system("notify-send -u critical -t 3000 error when collecting")


def GUI_leaves_clicks(
    d,
    d_activity,
    clicked_bounds,
    path_planner,
    d_package,
    testing_candidate_bounds_list,
    deviceId,
):

    # first click all clickable widgets on the screen
    # find clickable leaves
    xml1 = d.dump_hierarchy(compressed=True)
    leaves = click_points_Solver(xml1)

    clickable_bounds(xml1)
    for leaf in leaves:
        if leaf in clicked_bounds:
            continue
        d.click((leaf[0] + leaf[2]) / 2, (leaf[1] + leaf[3]) / 2)
        clicked_bounds.append(leaf)
        if d_package != d.current_package():
            logging.info(f"jummping out of current package {d_package}, pass")
            d.press("back")
            continue
        xml2 = d.dump_hierarchy(compressed=True)
        # d.sleep(0.5)

        if GUI_state_change(xml1, xml2):
            d.collect_data()
            logging.info("collected a pair")
            d.press("back")

        xml3 = d.dump_hierarchy(compressed=True)
        state_back = GUI_state_change(xml1, xml3)

        d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
        if d2_activity != d_activity or isLauncher2 or state_back:
            testing_candidate_bounds_list.append(leaf)
            path_planner.set_visited(d2_activity)
            full_cur_activity = path_planner.get_activity_full_path(d_activity)
            deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(
                d_package, full_cur_activity
            )
            launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)


def explore_cur_activity(d, deviceId, path_planner, timeout=60):
    d_activity, d_package, isLauncher = getActivityPackage(d)
    logging.info(f"exploring {d_activity}")
    # collect states of current activity
    # TODO ignore com.android.launcher3, org.chromium.webview_shell
    # com.android.permissioncontroller
    try:
        d.hide_keyboard()
        d.collect_data()
        logging.info(f"{GREEN}collected a pair{NC}")
    except Exception as e:
        logging.error(f"{RED}fail to collect data{NC}, {type(e).__name__}: {e}")

    path_planner.set_visited(d_activity)
    # first click all clickable widgets on the screen
    # clicked_bounds = []
    # testing_candidate_bounds_list = []
    # GUI_leaves_clicks(
    #     d,
    #     d_activity,
    #     clicked_bounds,
    #     path_planner,
    #     d_package,
    #     testing_candidate_bounds_list,
    #     deviceId,
    # )


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

    d.app_install(apk_path)

    d.app_start(pkg_name, wait=True)
    path_planner = PathPlanner(pkg_name, atg_json, deeplinks_json)
    unvisited = path_planner.get_unvisited_activity_deeplinks()

    # open launcher activity
    # TODO may faile BaseError
    dialogSolver(d)

    if unvisited is None:
        unvisited = []

    visited_rates.append(path_planner.get_visited_rate())

    start_time = datetime.now()
    for (activity, deeplinks, actions, params) in unvisited:
        logging.info(f"{YELLOW}trying to open{NC} {activity}")
        try:
            status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
            path_planner.set_popped(activity)

            # check activity
            if not d.is_running(activity):
                logging.error(f"{RED}fail to open target{NC}: {activity}")
                status = False

            if d.handle_syserr():
                logging.error(f"{RED}found system error prompt{NC}")
                status = False

            if status:
                path_planner.set_visited(activity)
                # key function here
                explore_cur_activity(d, deviceId, path_planner, timeout=60)
            else:
                d.app_stop(pkg_name)
        # VM/device crash
        except AdbError as e:
            logging.critical(f"device is probably offline, {e}")
            desktop_notification()
            input("===watting for reset connection manually===")
        except RuntimeError as e:
            if "is offline" in e:
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

            logging.critical(traceback.format_exc())
            logging.critical(f"skip {activity}, trying next activity")
            try:
                d.collect_data(definitions.ERROR_DIR)
            except Exception:
                logging.critical("unable to collect error data")

    delta = datetime.now() - start_time
    logging.info(f"visited rate:{path_planner.get_visited_rate()} in {delta}")
    path_planner.log_visited_rate(visited_rates, path=log_save_path)
    d.app_stop(pkg_name)
    return True


if __name__ == "__main__":
    # deviceId = '192.168.57.105'
    deviceId = "192.168.57.101:5555"
    # deviceId = 'cb8c90f4'
    # deviceId = 'VEG0220B17010232'
    name = "Lightroom"
    apk_path = os.path.join(definitions.REPACKAGE_DIR, f"{name}.apk")
    atg_json = os.path.join(definitions.ATG_DIR, f"{name}.json")
    deeplinks_json = definitions.DEEPLINKS_PATH
    log = os.path.join(definitions.VISIT_RATE_DIR, f"{name}.txt")

    unit_dynamic_testing(
        Device(deviceId), APK(apk_path), atg_json, deeplinks_json, log, reinstall=False
    )
