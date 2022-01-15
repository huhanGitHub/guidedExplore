import uiautomator2 as u2
import requests
from util import *
from dynamic_testing.testing_path_planner import PathPlanner
from dynamic_testing.hierachySolver import click_points_Solver, bounds2int
from dynamic_testing.grantPermissonDetector import dialogSolver
import subprocess
from datetime import datetime
from uiautomator2 import Direction


def random_dfs_explore(d, path_planner, timeout=30):
    d_activity, d_package, isLauncher = getActivityPackage(d)
    start_time = datetime.now()

    while True:
        path_planner.set_visited(d_activity)
        testing_candidate_bounds_list = []
        # find clickable leaves
        xml = d.dump_hierarchy(compressed=True)
        leaves = click_points_Solver(xml)
        for leaf in leaves:
            bounds = leaf.attrib.get('bounds')
            bounds = bounds2int(bounds)
            class_type = leaf.attrib.get('class')
            # print('click:', class_type)
            d.click((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
            d.sleep(1)

            d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
            if d2_activity != d_activity or isLauncher2:
                testing_candidate_bounds_list.append(bounds)
                path_planner.set_visited(d2_activity)
                # d.press('back')
                full_cur_activity = path_planner.get_activity_full_path(d_activity)
                d.app_start(d_package, full_cur_activity)

        cur_time = datetime.now()
        delta = (cur_time - start_time).seconds
        if delta > timeout:
            return
        else:
            next_activity = path_planner.pop_next_activity()
            if next_activity is not None:
                d.app_start(d_package, next_activity)
                # path_planner.set_visited(next_activity)
                d_activity, d_package, isLauncher = getActivityPackage(d)
            else:
                print('no next activity, exit')
                return


def unit_dynamic_testing(deviceId, apk_path, atg_json, test_time=300):
    installed1, packageName, mainActivity = installApk(apk_path, device=deviceId, reinstall=False)
    if installed1 != 0:
        print('install ' + apk_path + ' fail.')
        return
    try:
        d = u2.connect(deviceId)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return

    test_start_time = datetime.now()

    # open launcher activity
    d.app_start(packageName)
    d.sleep(3)
    dialogSolver(d)
    # d.swipe_ext(Direction.FORWARD)
    # d.swipe_ext(Direction.BACKWARD)
    path_planner = PathPlanner(atg_json)

    random_dfs_explore(d, path_planner, timeout=20)

    next_activity = path_planner.pop_next_activity()
    while next_activity is not None:
        d.app_start(packageName, next_activity)
        # d.swipe_ext(Direction.FORWARD)
        # d.swipe_ext(Direction.BACKWARD)
        random_dfs_explore(d, path_planner, timeout=20)
        next_activity = path_planner.pop_next_activity()
        print('---------------------- visited rate: ', path_planner.get_visited_rate())
        cur_test_time = datetime.now()
        delta = (cur_test_time - test_start_time).total_seconds()
        if delta > test_time:
            print('visited rate:%s in %s seconds' % (path_planner.get_visited_rate(), test_time))
            return


if __name__ == '__main__':
    deviceId = '192.168.57.101'
    apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks/BUSINESS/com.reflexisinc.dasess4110/ess_41_reflexis_one_v4.1..apk'
    atg_json = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/ATG/activity_match/atg/ess_41_reflexis_one_v4.1..apk.json'
    unit_dynamic_testing(deviceId, apk_path, atg_json)