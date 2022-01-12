import uiautomator2 as u2
import requests
from util import *
from dynamic_testing.testing_path_planner import PathPlanner





def unit_dynamic_testing(deviceId, apk_path, atg_json):
    installed1, packageName, mainActivity = installApk(apk_path, device=deviceId, reinstall=False)
    if installed1 != 0:
        print('install ' + apk_path + ' fail.')
        return
    try:
        d = u2.connect(deviceId)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return

    # open launcher activity
    d.app_start(packageName)

    d_activity, d_package, isLauncher = getActivityPackage(d)
    path_planner = PathPlanner(atg_json)
    path_planner.set_visited(d_activity)
    next_activity = path_planner.pop_next_activity()
    # print(next_activity)
    d.app_start(packageName, next_activity)



if __name__ == '__main__':
    deviceId = '192.168.57.103'
    apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks/BUSINESS/com.reflexisinc.dasess4110/ess_41_reflexis_one_v4.1..apk'
    atg_json = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/ATG/activity_match/atg/ess_41_reflexis_one_v4.1..apk.json'
    unit_dynamic_testing(deviceId, apk_path, atg_json)