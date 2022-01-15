import os
import subprocess
import json

intent_error_msg = 'Error: Activity not started'


def read_deeplinks(deeplink):
    with open(deeplink, 'r', encoding='utf8') as f:
        deeplinks = json.dumps(f.read())
        return deeplinks


# adb shell am start -a android.intent.action.VIEW -d com_example_hanhu://com.example.hanhu.SettingsActivity --es textview1 "I\ am\ from\ adb" -e textview2 "from\ adb"
def launch_activity_by_deeplink(deviceId, deeplink, action, params):
    cmd = 'adb -s ' + deviceId + ' shell am start -W -a ' + action + ' -d ' + deeplink
    if len(params) != 0:
        params_cmd = ' '.join(params)
        cmd = cmd + ' ' + params_cmd

    try:
        p = subprocess.run(cmd, shell=True, timeout=8, capture_output=True).stdout

        if intent_error_msg in str(p) or intent_error_msg in str(p):
            print('intent fail')
            return False
    except subprocess.TimeoutExpired:
        print('cmd timeout')
        return False
