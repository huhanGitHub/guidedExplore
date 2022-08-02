import subprocess
import json
import logging

intent_error_msg = "Error: Activity not started"
intent_success_msg = "Status: ok"


def read_deeplinks(deeplink):
    with open(deeplink, "r", encoding="utf8") as f:
        deeplinks = json.dumps(f.read())
        return deeplinks


# adb shell am start -a android.intent.action.VIEW -d com_example_xxx://com.example.xxx.SettingsActivity --es textview1 "I\ am\ from\ adb" -e textview2 "from\ adb"
def launch_activity_by_deeplink(deviceId, deeplink, action, params):
    cmd = "adb -s " + deviceId + " shell am start -W -a " + action + " -d " + deeplink
    if len(params) != 0:
        params_cmd = " ".join(params)
        cmd = f"{cmd} {params_cmd}"

    try:
        p = subprocess.run(cmd, shell=True, timeout=5, capture_output=True).stdout
        if intent_success_msg in str(p):
            return (deviceId, deeplink, action, params)
    except subprocess.TimeoutExpired:
        logging.debug(f"cmd timeout: {deeplink}")

    return False


def launch_activity_by_deeplinks(deviceId, deeplinks, actions, params):
    launch_status = False
    if deeplinks is None or actions is None:
        return launch_status
    for deeplink, action in zip(deeplinks, actions):
        status = launch_activity_by_deeplink(deviceId, deeplink, action, params)
        if status:
            launch_status = status
            break

    return launch_status
