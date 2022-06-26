#!/usr/bin/env python3
import logging
import os
import shutil
import time

from pyaxmlparser import APK

from decompile_apk import unit_decompile
import definitions
from definitions import (APK_DIR, DATA_DIR, DECOMPILE_DIR, DEEPLINKS_PATH,
                         REPACKAGE_DIR)
from run_preprocess import unit_run_preprocess
from GUI_data_collection.run_data_collection import unit_dynamic_testing


def _apk_paths(dir=APK_DIR):
    apks = sorted(os.listdir(dir))
    apks = map(lambda x: os.path.join(dir, x), apks)
    apks = [f for f in apks if os.path.splitext(f)[1] == '.apk']
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


def preprocess():
    apks = _decompiled_paths()

    for i in list(enumerate(apks + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apks):
        return
    else:
        apk_path = unit_run_preprocess(apks[i], DECOMPILE_DIR, REPACKAGE_DIR, DEEPLINKS_PATH, DATA_DIR)
        apksigner = '~/Android/Sdk/build-tools/30.0.3/apksigner'
        key = '~/.android/debug.keystore'
        sign_cmd = f'{apksigner} sign --ks {key} --ks-pass pass:android --key-pass pass:android {apk_path}'
        os.system(sign_cmd)
        logging.info(f"signed {apk_path}")


def nothing():
    pass


def install():
    tablet = definitions.device
    apk_paths = _repackaged_paths() + _apk_paths()

    for i in list(enumerate(apk_paths + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apk_paths):
        return
    else:
        tablet.app_install(apk_paths[i])
        name = APK(apk_paths[i]).package
        tablet.app_start(name)


def screenshots():
    tablet = definitions.device
    t = str(int(time.time()))
    out_dir = os.path.join(DATA_DIR, t)
    tablet.save(out_dir)


def cur():
    tablet = definitions.device
    print(str(tablet.app_current()) + "\n")


def explore():
    apk_paths = _repackaged_paths()

    for i in list(enumerate(apk_paths + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apk_paths):
        return
    else:
        name = os.path.basename(apk_paths[i])
        name = os.path.splitext(name)[0]
        apk_path = os.path.join(definitions.REPACKAGE_DIR, f'{name}.apk')
        atg_json = os.path.join(definitions.ATG_DIR, f'{name}.json')
        deeplinks_json = definitions.DEEPLINKS_PATH
        log = os.path.join(definitions.VISIT_RATE_DIR, f'{name}.txt')

        unit_dynamic_testing(definitions.VM_ID, apk_path, atg_json, deeplinks_json, log, reinstall=False)


def cli():
    d = {
        "decompile apk": decompile,
        "preprocess unziped apk": preprocess,
        "install app": install,
        "explore repackaged apk": explore,
        "screenshot": screenshots,
        "current app": cur,
        "refresh": nothing,
    }

    while True:
        cmds = list(d)
        for i in list(enumerate(cmds)):
            print(i)
        i = int(input("Enter a index: "))
        d[cmds[i]]()


if __name__ == '__main__':
    cli()
    # TODO unit_run_preprocess discovering entire folder, duplicated work
    # TODO error handle

    # print(definitions.device.info)
    # print(definitions.device.device_type())
