import logging
import random
from datetime import datetime

import uiautomator2.exceptions
from uiautomator2 import Direction
from utils.util import *
from GUI_data_collection import Device

from activity_launcher import launch_activity_by_deeplinks
from dynamic_testing.grantPermissonDetector import dialogSolver
from dynamic_testing.hierachySolver import click_points_Solver
from dynamic_testing.testing_path_planner import PathPlanner


def random_bfs_explore(d, deviceId, package_name, path_planner, timeout=60, collect_GUI=False):

    d_activity, d_package, isLauncher = getActivityPackage(d)
    start_time = datetime.now()
    random_status = False

    # judge if the screen can swipe
    swipe = False
    xml = d.dump_hierarchy(compressed=True)

    leaves = click_points_Solver(xml)
    d.swipe_ext(Direction.FORWARD)
    xml2 = d.dump_hierarchy(compressed=True)
    leaves2 = click_points_Solver(xml2)
    leaves.sort()
    leaves2.sort()
    new_leaves_not_in_leaves = [i for i in leaves2 if i not in leaves]
    if len(new_leaves_not_in_leaves) > 2:
        swipe = True
        d.swipe_ext(Direction.BACKWARD)

    clicked_bounds = []
    cur_timeout = timeout
    while True:
        cur_time = datetime.now()
        delta = (cur_time - start_time).seconds
        if delta > cur_timeout:
            return

        # random testing, click clickable pixel on the screen randomly
        if random_status:
            cur_d_activity, cur_d_package, cur_isLauncher = getActivityPackage(d)
            path_planner.set_visited(cur_d_activity)
            if cur_d_activity != d_activity or cur_d_package != package_name:
                full_cur_activity = path_planner.get_activity_full_path(d_activity)
                # d.app_start(d_package, full_cur_activity)
                deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                            full_cur_activity)
                status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)

            direction_list = [0, 1, 2, 2, 2]
            dire = random.choice(direction_list)
            if dire == 0:
                d.swipe_ext(Direction.FORWARD)
            elif dire == 1:
                d.swipe_ext(Direction.BACKWARD)

            xml = d.dump_hierarchy(compressed=True)
            leaves = click_points_Solver(xml)
            if len(leaves) == 0:
                d.press('back')
                continue

            cur_timeout = len(leaves) * 6
            cur_timeout = max(50, cur_timeout)
            cur_timeout = min(cur_timeout, 200)
            print('cur_timeout ' + str(cur_timeout))
            # not_click_leaves = [i for i in leaves if i not in clicked_bounds]
            # if len(not_click_leaves) == 0:
            #     d.press('back')
            #     continue
            action_point = random.choice(leaves)
            d.click((action_point[0] + action_point[2]) / 2, (action_point[1] + action_point[3]) / 2)
            #clicked_bounds.append(action_point)
            try:
                xml2 = d.dump_hierarchy(compressed=True)
            except uiautomator2.exceptions.JSONRPCError as e:
                print('java.lang.OutOfMemoryError')
                d.press('back')
                continue
            except requests.exceptions.ConnectTimeout as e2:
                print('HTTPConnectionPool')
                continue

            new_leaves = click_points_Solver(xml2)
            leaves.sort()
            new_leaves.sort()
            new_leaves_not_in_leaves = [i for i in new_leaves if i not in leaves]
            d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
            if len(new_leaves_not_in_leaves) >= 3 and d2_activity == d_activity:
                action_point = random.choice(new_leaves_not_in_leaves)
                d.click((action_point[0] + action_point[2]) / 2, (action_point[1] + action_point[3]) / 2)
                # new state, update the clicked bounds


        # first click all clickable widgets on the screen
        else:
            path_planner.set_visited(d_activity)
            testing_candidate_bounds_list = []
            # find clickable leaves
            xml = d.dump_hierarchy(compressed=True)
            leaves = click_points_Solver(xml)
            for leaf in leaves:
                if leaf in clicked_bounds:
                    continue
                d.click((leaf[0] + leaf[2]) / 2, (leaf[1] + leaf[3]) / 2)
                clicked_bounds.append(leaf)
                # d.sleep(0.5)

                d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
                if d2_activity != d_activity or isLauncher2:
                    testing_candidate_bounds_list.append(leaf)
                    path_planner.set_visited(d2_activity)
                    # d.press('back')
                    full_cur_activity = path_planner.get_activity_full_path(d_activity)
                    # d.app_start(d_package, full_cur_activity)
                    deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                                full_cur_activity)
                    status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)

            if swipe:
                d.swipe_ext(Direction.FORWARD)
                xml2 = d.dump_hierarchy(compressed=True)
                leaves2 = click_points_Solver(xml2)
                for leaf in leaves2:
                    d.click((leaf[0] + leaf[2]) / 2, (leaf[1] + leaf[3]) / 2)
                    clicked_bounds.append(leaf)
                    # d.sleep(0.5)

                    d2_activity, d2_package, isLauncher2 = getActivityPackage(d)
                    if d2_activity != d_activity or isLauncher2:
                        testing_candidate_bounds_list.append(leaf)
                        path_planner.set_visited(d2_activity)
                        # d.press('back')
                        full_cur_activity = path_planner.get_activity_full_path(d_activity)
                        # d.app_start(d_package, full_cur_activity)
                        deeplinks, actions, params = path_planner.get_deeplinks_by_package_activity(d_package,
                                                                                                    full_cur_activity)
                        status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)

                d.swipe_ext(Direction.BACKWARD)

            # after clicking all clickable widgets, begin to randomly click and test
            random_status = True


def unit_dynamic_testing(deviceId, apk_path, atg_json, deeplinks_json, log_save_path, test_time=1200, reinstall=True):
    visited_rate = []
    installed1, packageName, mainActivity = installApk(apk_path, device=deviceId, reinstall=reinstall)
    if installed1 != 0:
        print('install ' + apk_path + ' fail.')
        return
    try:
        d = Device(deviceId)
        d.app_install(apk_path)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return

    test_start_time = datetime.now()

    # open launcher activity
    # assert packageName == 'com.explorer.file.manager.fileexplorer.exfile'
    d.app_start(packageName)
    d.sleep(3)
    dialogSolver(d)
    # d.swipe_ext(Direction.FORWARD)
    # d.swipe_ext(Direction.BACKWARD)
    path_planner = PathPlanner(packageName, atg_json, deeplinks_json)
    delta = 0
    while delta <= test_time:
        random_bfs_explore(d, deviceId, packageName, path_planner, timeout=60)
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
                    cur_test_time = datetime.now()
                    delta = (cur_test_time - test_start_time).total_seconds()
                    print('time cost:' + str(delta))
                    return
                else:
                    for i in unvisited:
                        activity, deeplinks, actions, params = i
                        status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
                        path_planner.set_popped(activity)
                        if status:
                            path_planner.set_visited(activity)
                            random_bfs_explore(d, deviceId, packageName, path_planner, timeout=60)
                            break

        cur_test_time = datetime.now()
        delta = (cur_test_time - test_start_time).total_seconds()

    print('visited rate:%s in %s seconds' % (path_planner.get_visited_rate(), test_time))
    path_planner.log_visited_rate(visited_rate, path=log_save_path)
    return


def unit_dynamic_testing_package(deviceId, apk_path, atg_json, deeplinks_json, log_save_path, packageName, test_time=1200):
    visited_rate = []

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
        random_bfs_explore(d, deviceId, packageName, path_planner, timeout=60)
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
                    cur_test_time = datetime.now()
                    delta = (cur_test_time - test_start_time).total_seconds()
                    print('time cost:' + str(delta))
                    return
                else:
                    for i in unvisited:
                        activity, deeplinks, actions, params = i
                        status = launch_activity_by_deeplinks(deviceId, deeplinks, actions, params)
                        path_planner.set_popped(activity)
                        if status:
                            path_planner.set_visited(activity)
                            random_bfs_explore(d, deviceId, packageName, path_planner, timeout=60)
                            break

        cur_test_time = datetime.now()
        delta = (cur_test_time - test_start_time).total_seconds()

    print('visited rate:%s in %s seconds' % (path_planner.get_visited_rate(), test_time))
    path_planner.log_visited_rate(visited_rate, path=log_save_path)
    return


if __name__ == '__main__':
    # deviceId = '192.168.57.105'
    deviceId = '192.168.57.101:5555'
    # deviceId = 'cb8c90f4'
    # deviceId = 'VEG0220B17010232'
    name = 'Lightroom'
    apk_path = f'./data/repackaged_apks/{name}.apk'
    atg_json = f'./data/activity_atg/{name}.json'
    deeplinks_json = r'./data/deeplinks_params.json'
    log = f'./data/visited_rate/{name}.txt'

    # log in the app in advance and set the parameter reinstall as false to explore app with login
    # there may be unpredictable issues, so pls run each app multiple times.
    # logging in and granting permission in advance will help a lot
    while True:
        try:
            unit_dynamic_testing(deviceId, apk_path, atg_json, deeplinks_json, log, reinstall=False)
        except Exception as e:
            # type(e).__name__
            logging.error(e)
