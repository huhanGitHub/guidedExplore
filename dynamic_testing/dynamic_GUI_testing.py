import random

import uiautomator2 as u2
import requests
from util import *
from dynamic_testing.testing_path_planner import PathPlanner
from dynamic_testing.hierachySolver import click_points_Solver, bounds2int
from dynamic_testing.grantPermissonDetector import dialogSolver
import subprocess
from datetime import datetime
from uiautomator2 import Direction
from activity_launcher import launch_activity_by_deeplinks, launch_activity_by_deeplink


def random_dfs_explore(d, deviceId, path_planner, timeout=30):
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
                # d.app_start(d_package, full_cur_activity)
                deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                            full_cur_activity)
                status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)

        cur_time = datetime.now()
        delta = (cur_time - start_time).seconds
        if delta > timeout:
            return
        else:
            if len(testing_candidate_bounds_list) == 0:
                return
            else:
                click_bounds = random.sample(testing_candidate_bounds_list, 1)[0]
                d.click((click_bounds[0] + click_bounds[2]) / 2, (click_bounds[1] + click_bounds[3]) / 2)
                d_activity, d_package, isLauncher = getActivityPackage(d)
                if isLauncher:
                    return


def unit_dynamic_testing(deviceId, apk_path, atg_json, deeplinks_json, log_save_path, test_time=600):
    visited_rate = []
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
    path_planner = PathPlanner(packageName, atg_json, deeplinks_json)
    delta = 0
    while delta <= test_time:
        random_dfs_explore(d, deviceId, path_planner, timeout=20)
        print('---------------------- visited rate: ', path_planner.get_visited_rate())
        visited_rate.append(path_planner.get_visited_rate())

        while True:
            next_activity = path_planner.pop_next_activity()
            if next_activity is not None:
                # d.app_start(d_package, next_activity)
                deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(packageName,
                                                                                            next_activity)
                status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
                if status:
                    path_planner.set_visited(next_activity)
                    break

            else:
                print('no next activity in ATG')
                unvisited = path_planner.get_unvisited_activity_deeplinks()
                if unvisited is None:
                    print('no activity, finish')
                    print('visited rate:%s' % (path_planner.get_visited_rate()))
                    visited_rate.append(path_planner.get_visited_rate())
                    path_planner.log_visited_rate(visited_rate, path=log_save_path)
                    return
                else:
                    for i in unvisited:
                        activity, deeplinks, actions, params = i
                        status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
                        path_planner.set_popped(activity)
                        if status:
                            path_planner.set_visited(activity)
                            break

        cur_test_time = datetime.now()
        delta = (cur_test_time - test_start_time).total_seconds()

    print('visited rate:%s in %s seconds' % (path_planner.get_visited_rate(), test_time))
    path_planner.log_visited_rate(visited_rate, path=log_save_path)
    return


if __name__ == '__main__':
    deviceId = '192.168.57.101'
    # deviceId = 'cb8c90f4'
    apk_path = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/repackaged_apks/ez.apk'
    atg_json = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/activity_atg/ez.json'
    deeplinks_json = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/deeplinks_params.json'
    log = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/visited_rate/ez.txt'
    unit_dynamic_testing(deviceId, apk_path, atg_json, deeplinks_json, log)
