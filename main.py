#!/usr/bin/env python3
import logging
import os
import shutil
import time

from pyaxmlparser import APK

import definitions
from uiautomator2 import GatewayError
from decompile_apk import unit_decompile
from definitions import APK_DIR, DATA_DIR, DECOMPILE_DIR, DEEPLINKS_PATH, REPACKAGE_DIR
from GUI_data_collection.run_data_collection import unit_dynamic_testing
from run_preprocess import unit_run_preprocess, unit_run_preprocess_one
from utils.device import Device
from utils.util import installApk


def _apk_paths(dir=APK_DIR):
    apks = sorted(os.listdir(dir))
    apks = map(lambda x: os.path.join(dir, x), apks)
    apks = [f for f in apks if os.path.splitext(f)[1] == ".apk"]
    return apks


def _repackaged_paths():
    return _apk_paths(REPACKAGE_DIR)


def _decompiled_paths():
    apks = sorted(os.listdir(DECOMPILE_DIR))
    apks = map(lambda x: os.path.join(DECOMPILE_DIR, x), apks)
    apks = [f for f in apks if os.path.isdir(f)]
    return apks


def decompile():
    apks = _apk_paths()

    for i in list(enumerate(apks + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apks):
        return
    else:
        apk_name = APK(apks[i]).package
        save_path = os.path.join(DECOMPILE_DIR, apk_name)
        # recreate save_path
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        os.mkdir(save_path)
        unit_decompile(apks[i], save_path)


def all_in_one():
    apks = _apk_paths()

    for i in list(enumerate(apks + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apks):
        return
    else:
        apk_name = APK(apks[i]).package
        save_path = os.path.join(DECOMPILE_DIR, apk_name)
        # recreate save_path
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        os.mkdir(save_path)
        unit_decompile(apks[i], save_path)

        de_path = os.path.join(DECOMPILE_DIR, apk_name)
        apk_path = unit_run_preprocess(
            de_path, DECOMPILE_DIR, REPACKAGE_DIR, DEEPLINKS_PATH, DATA_DIR
        )
        apksigner = "~/Android/Sdk/build-tools/30.0.3/apksigner"
        key = "~/.android/debug.keystore"
        sign_cmd = f"{apksigner} sign --ks {key} --ks-pass pass:android --key-pass pass:android {apk_path}"
        os.system(sign_cmd)
        logging.info(f"signed {apk_path}")

        # definitions.device.app_install(apk_path)
        installApk(apk_path, reinstall=True)
        definitions.get_device().app_start(apk_name)


def preprocess(apk_path):
    package_name = APK(apk_path).package
    decom_path = os.path.join(DECOMPILE_DIR, package_name)
    # recreate save_path
    if os.path.exists(decom_path):
        shutil.rmtree(decom_path)
    os.mkdir(decom_path)
    unit_decompile(apk_path, decom_path)

    repackaged_path = unit_run_preprocess_one(
        decom_path, REPACKAGE_DIR, DEEPLINKS_PATH, DATA_DIR
    )
    return repackaged_path


def preprocess_cli():
    apks = _decompiled_paths()

    for i in list(enumerate(apks + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apks):
        return
    else:
        apk_path = unit_run_preprocess(
            apks[i], DECOMPILE_DIR, REPACKAGE_DIR, DEEPLINKS_PATH, DATA_DIR
        )
        apksigner = "~/Android/Sdk/build-tools/30.0.3/apksigner"
        key = "~/.android/debug.keystore"
        sign_cmd = f"{apksigner} sign --ks {key} --ks-pass pass:android --key-pass pass:android {apk_path}"
        os.system(sign_cmd)
        logging.info(f"signed {apk_path}")


def nothing():
    pass


def install():
    tablet = definitions.get_device()
    apk_paths = _repackaged_paths() + _apk_paths()

    for i in list(enumerate(apk_paths + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apk_paths):
        return
    else:
        installApk(apk_paths[i], reinstall=True)
        name = APK(apk_paths[i]).package
        tablet.app_start(name)


def screenshots():
    tablet = definitions.get_device()
    t = str(int(time.time()))
    out_dir = os.path.join(DATA_DIR, t)
    tablet.save(out_dir)


def cur():
    tablet = definitions.get_device()
    print(str(tablet.app_current()) + "\n")


def is_preprocessed(package_name):
    if not os.path.exists(
        os.path.join(definitions.ATG_DIR, f'{package_name}.json')
    ):
        logging.error(f'did not found atg file for {package_name}')
        return False
    if not os.path.exists(
        os.path.join(definitions.REPACKAGE_DIR, f'{package_name}.apk.idsig')
    ):
        logging.error(f'did not found signature file for {package_name}')
        return False
    return True


def basename_no_ext(path):
    return os.path.basename((os.path.splitext(path)[0]))


def explore(apk_path):
    """
    :param apk_path: recompiled apk path
    """
    name = basename_no_ext(apk_path)
    logging.info(f"exploring {name}")

    apk_path = os.path.join(definitions.REPACKAGE_DIR, f"{name}.apk")
    atg_json = os.path.join(definitions.ATG_DIR, f"{name}.json")
    deeplinks_json = definitions.DEEPLINKS_PATH
    log = os.path.join(definitions.VISIT_RATE_DIR, f"{name}.txt")

    if not is_preprocessed(name):
        raise RuntimeError("proprocess may failed, cannot explore")

    unit_dynamic_testing(
        definitions.VM_ID,
        apk_path,
        atg_json,
        deeplinks_json,
        log,
        reinstall=True,
    )


def explore_cli():
    apk_paths = _repackaged_paths()

    for i in list(enumerate(apk_paths + ["exit"])):
        print(i)
    # i = int(input("Enter a index: "))
    i = 2
    if i == len(apk_paths):
        return
    else:
        explore(apk_paths[i])


def cli():
    d = {
        "decompile apk": decompile,
        "preprocess unziped apk": preprocess_cli,
        "install app": install,
        "all in one": all_in_one,
        "explore repackaged apk": explore_cli,
        "current app": cur,
        "refresh": nothing,
    }

    while True:
        cmds = list(d)
        for i in list(enumerate(cmds)):
            print(i)
        i = int(input("Enter a index: "))
        d[cmds[i]]()


def collect_one_app(device: Device, package_name):
    """
    prerequest: package is install on device
    """
    device.app_start(package_name)
    pass


def test():
    # REVIEW unit_run_preprocess discovering entire folder, duplicated work
    # TODO error handle
    # TODO keyboard
    # TODO kill when exit
    # TODO check webview element
    # 0. Preprocess all apks under a folder
    # 1. Open 1 injected app
    # explore_cli()
    try:
        apk_path = os.path.join(APK_DIR, 'com.move.realtor.apk')
        # repack_path = preprocess(apk_path)
        repack_path = os.path.join(REPACKAGE_DIR, 'com.move.realtor.apk')
        explore(repack_path)
    except KeyboardInterrupt:
        logging.info("exiting")
    except RuntimeError as e:
        logging.error(e)


if __name__ == "__main__":
    # cli()
    test()
