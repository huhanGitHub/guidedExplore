import logging
import os
import shutil
import threading

from pyaxmlparser import APK

import definitions
from decompile_apk import unit_decompile
from definitions import APK_DIR, DATA_DIR, DECOMPILE_DIR, REPACKAGE_DIR
from GUI_data_collection.run_data_collection import unit_dynamic_testing
from run_preprocess import unit_run_preprocess_one
from utils.device import Device
from utils.util import installApk
from utils.xml_helpers import click_if_find
from utils.path import basename_no_ext

from phone import collect_data

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
    if i != len(apks):
        apk_name = APK(apks[i]).package
        save_path = os.path.join(DECOMPILE_DIR, apk_name)
        # recreate save_path
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        os.mkdir(save_path)
        unit_decompile(apks[i], save_path)


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


def preprocess_cli():
    apks = _apk_paths()

    for i in list(enumerate(apks + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apks):
        return
    else:
        preprocess(apks[i])


def nothing():
    pass


def install():
    tablet = definitions.get_device()
    apk_paths = _apk_paths()

    for i in list(enumerate(apk_paths + ["exit"])):
        print(i)
    i = int(input("Enter a index: "))
    if i == len(apk_paths):
        return
    else:
        installApk(apk_paths[i], reinstall=True)
        name = APK(apk_paths[i]).package
        tablet.app_start(name)


def collect_cur():
    tablet = definitions.get_device()
    tablet.to_phone()
    collect_data(tablet)
    # tablet.to_tablet()
    print(str(tablet.app_current()) + "\n")


def is_preprocessed(package_name):
    if not os.path.exists(
        os.path.join(definitions.DEEPLINKS_DIR, f"{package_name}.json")
    ):
        logging.error(f"did not found deeplinks file for {package_name}")
        return False
    if not os.path.exists(
        os.path.join(definitions.ATG_DIR, f"{package_name}.json")
    ):
        logging.error(f"did not found atg file for {package_name}")
        return False
    if not os.path.exists(
        os.path.join(definitions.REPACKAGE_DIR, f"{package_name}.apk")
    ):
        logging.error(f"did not found signature file for {package_name}")
        return False
    if not os.path.exists(
        os.path.join(definitions.REPACKAGE_DIR, f"{package_name}.apk.idsig")
    ):
        logging.error(f"did not found signature file for {package_name}")
        return False
    return True


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

def find_click():
    device = definitions.get_device()
    txt = input(":")
    click_if_find(device, {"text": txt})

def change():
    definitions.get_device().change_device_type()

def clear():
    definitions.get_device().app_uninstall_all()

def cli():
    em = Device(definitions.EM_ID, False, False)
    definitions._device = em
    d = {
        # "preprocess unziped apk": preprocess_cli,
        "install app": install,
        # "explore repackaged apk": explore_cli,
        "save current": collect_cur,
        # "decompile apk": decompile,
        "find_click": find_click,
        "refresh": nothing,
        "change": change,
        "clear": clear
    }

    while True:
        cmds = list(d)
        for i in list(enumerate(cmds)):
            print(i)
        i = int(input("Enter a index: "))
        d[cmds[i]]()


def is_explored(package_name):
    return os.path.exists(definitions.OUT_DIR, package_name)


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
        f.write('\n')


def unexplored_apks():
    explored_apps = [f.name for f in os.scandir(definitions.OUT_DIR) if f.is_dir()]
    failed_apps = [f for f in open(definitions.FAIL_LOG_PATH).read().splitlines()]
    ignored_apps = set(explored_apps).union(set(failed_apps))
    apks = [f.path for f in os.scandir(definitions.APK_DIR)
            if f.name.endswith(".apk") and f.name.removesuffix(".apk") not in ignored_apps]
    return apks


def run_one(device, shared_apks):
    pass


def multi_run(devices):
    lock = threading.Lock()
    apks = unexplored_apks()
    print(apks)
    print(len(apks))

    def pop_apk():
        lock.acquire()
        apk = apks.pop()
        lock.release()
        return apk
    threads = [threading.Thread(run_one, (d, apks, pop_apk)) for d in devices]
    for i in threads:
        i.start()

    for i in threads:
        i.join()


def run(device, apk=None):
    """
    explore one apk or apks under `definitions.APK_DIR`
    example: apk=os.path.join(definitions.APK_DIR, "com.duolingo.apk")
    """
    # TODO check os.system commands if multi connected devices
    if apk is None:
        apks = unexplored_apks()
        print(apks)
        print(len(apks))
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
            else:
                logging.critical(f"error when processing {basename_no_ext(apk_path)}, {type(e).__name__}:{e}")
                import traceback
                logging.debug(traceback.format_exc())
                log_failure(basename_no_ext(apk_path))
        except Exception as e:
            logging.critical(f"error when processing {basename_no_ext(apk_path)}, {type(e).__name__}:{e}")
            import traceback
            logging.debug(traceback.format_exc())
            log_failure(basename_no_ext(apk_path))
        finally:
            device.app_stop_all()
            device.app_uninstall(name)


def main():
    apk = None
    apk = os.path.join(definitions.APK_DIR, "com.twitter.android.apk")
    # em = Device(definitions.EM_ID, False, True)
    em = definitions.get_device()
    run(em, apk)

if __name__ == "__main__":
    # cli()
    main()
