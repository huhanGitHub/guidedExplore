# encoding: utf8
import json
import os
import subprocess
import time
from difflib import SequenceMatcher

import requests
from pyaxmlparser import APK

import uiautomator2 as u2


def connectionAdaptor(phoneDevice, tabletDevice):
    try:
        d1 = u2.connect(phoneDevice)
        d2 = u2.connect(tabletDevice)
        return d1, d2, True
    except requests.exceptions.ConnectionError:
        print("requests.exceptions.ConnectionError")
        return None, None, False


def installApk(apkPath, device=None, reinstall=True):
    packageName, mainActivity = getPackageByApk(apkPath)

    if reinstall:
        # check if installed
        prefixCmd = "adb "
        if device is not None:
            print("device: " + device)
            prefixCmd = prefixCmd + "-s " + device

        command1 = prefixCmd + " shell pm list packages -3"
        packages = subprocess.check_output(
            command1, shell=True, stderr=subprocess.STDOUT
        ).decode("utf-8")
        packages = packages.replace("package:", "").strip()
        packages = packages.replace("\r", "").strip()
        packages = packages.split("\n")
        if packageName in packages:
            print(packageName + " has installed, begin to uninstall it")
            command2 = prefixCmd + " uninstall " + packageName
            out = subprocess.check_output(
                command2, shell=True, stderr=subprocess.STDOUT
            ).decode("utf-8")
            print("uninstall success")

        # begin to install apk
        command3 = prefixCmd + " install " + apkPath
        # os.system(command3)
        try:
            out = subprocess.check_output(
                command3, shell=True, stderr=subprocess.STDOUT, timeout=25
            ).decode("utf-8")
            print("install " + apkPath + " success")
            return 0, packageName, mainActivity
        except subprocess.CalledProcessError as e:
            print("install apk error: " + apkPath)
            out = e.output.decode("utf-8")
            print(out)
            # 'adb: failed to install apks/VidMate.apk: Failure [INSTALL_FAILED_ALREADY_EXISTS: Attempt to re-install
            # com.nemo.vidmate without first uninstalling.]
            return 1, packageName, mainActivity
        except FileNotFoundError:
            print("file not found: " + apkPath)
            return 1, packageName, mainActivity
        except subprocess.TimeoutExpired:
            print("cmd timeout， install fail")
            return 1, packageName, mainActivity

    else:
        return 0, packageName, mainActivity


def getPackageByApk(apkPath):
    apkf = APK(apkPath)
    package = apkf.get_package()
    mainActivity = apkf.get_main_activity()
    return package, mainActivity


def getActivityPackage(d):
    isLauncher = False
    try:
        d_current = d.app_current()
    except OSError as e:
        print(e)
        return None, None, None
    d_package = d_current["package"]
    d_activity = d_current["activity"]
    if "android" in d_activity and "Launcher" in d_activity:
        isLauncher = True
    # NOTE: require names are in Android standard.
    d_activity = d_activity[d_activity.rindex(".") + 1 :]
    return d_activity, d_package, isLauncher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def save_screen_data(saveDir, xml1, xml2, img1, img2, activity_name, package_name):
    if img1 is None or img2 is None:
        print("none img, save fail, return")
        return

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)

    def getPath(devicetype, filetype):
        return os.path.join(
            saveDir, f"{package_name}_{activity_name}_{devicetype}.{filetype}"
        )

    xml1Path = getPath("phone", "xml")
    img1Path = getPath("phone", "png")
    xml2Path = getPath("tablet", "xml")
    img2Path = getPath("tablet", "png")

    with open(xml1Path, "w+", encoding="utf8") as f1, open(
        xml2Path, "w+", encoding="utf8"
    ) as f2:
        f1.write(xml1)
        f2.write(xml2)
        img1.save(img1Path)
        img2.save(img2Path)


def xmlScreenSaver_single(saveDir, xml1, img1, activity1):
    if img1 is None:
        print("none img, save fail, return")
        return

    t = int(time.time())
    xml1Name = "phone_" + str(t) + "_" + activity1 + ".xml"
    img1Name = "phone_" + str(t) + "_" + activity1 + ".png"
    xml1Path = os.path.join(saveDir, xml1Name)
    img1Path = os.path.join(saveDir, img1Name)

    with open(xml1Path, "a", encoding="utf8") as f1:
        f1.write(xml1)
        img1.save(img1Path)


def shorterFilename(saveDir):
    index = 0
    for root, dirs, files in os.walk(saveDir):
        for file in files:
            if str(file).endswith(".apk") or str(file).endswith(".xapk"):
                filePath = os.path.join(root, file)
                fields = file.split(".")
                extention = fields[-1]
                name = ".".join(fields[:-1])
                if len(name) > 25:
                    name = name[:25]
                name = name.replace(" ", "_")
                name = name.replace("\\", "")
                newFile = name + "." + extention
                newFilePath = os.path.join(root, newFile)
                try:
                    os.rename(filePath, newFilePath)
                except FileExistsError:
                    print("exist, new name")
                    newFile = name + str(index) + "." + extention
                    index += 1
                    newFilePath = os.path.join(root, newFile)
                    os.rename(filePath, newFilePath)
                except OSError:
                    print("os error")


def safeScreenshot(d):
    try:
        img = d.screenshot()
        return img
    except Exception:
        return None


# return value 0 success, 1 install fail, 2 no the same texts, 3 time out, 4 fail others, 5 no tablet adaption
def apksUninstall(apkPath, d1, d2, d1_packages, d2_packages):
    # 0 success, 1 install fail
    packageName, mainActivity = getPackageByApk(apkPath)
    # d1_packages = d1.app_list()
    # d2_packages = d2.app_list()
    if packageName in d1_packages:
        d1.app_stop(packageName)
        d1.app_uninstall(packageName)
        print("uninstall " + packageName)
    if packageName in d2_packages:
        d2.app_stop(packageName)
        d2.app_uninstall(packageName)
        print("uninstall " + packageName)

    return 0


def uninstallApks(
    apksDir=r"/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks",
    device1Id="cb8c90f4",
    device2Id="R52RA0C2MFF",
    log=r"log.txt",
):
    delimiter = (" ||| ",)
    apks = ({},)
    index = (0,)
    d1, d2, connectStatus = connectionAdaptor(device1Id, device2Id)
    while not connectStatus:
        d1, d2, connectStatus = connectionAdaptor(device1Id, device2Id)

    d1_packages = d1.app_list()
    d2_packages = d2.app_list()

    with open(log, "a+", encoding="utf8") as f:
        for root, dirs, files in os.walk(apksDir):
            for file in files:
                if file.endswith(".apk") or file.endswith(".xapk"):
                    print("apk " + str(index))
                    index += 1
                    if index <= 1253:
                        continue
                    filePath = os.path.join(root, file)

                    try:
                        ret = apksUninstall(filePath, d1, d2, d1_packages, d2_packages)
                    except StopIteration:
                        print("time out " + file)
                        apks[file] = 3
                        f.write(file + delimiter + "3" + "\n")
                    except Exception:
                        print("fail other " + file)
                        apks[file] = 4
                        f.write(file + delimiter + "4" + "\n")


def uninstallApks_single(apk_dir, deviceId):
    log = r"log.txt"
    delimiter = " ||| "
    apks = {}
    index = 0

    d1 = u2.connect(deviceId)
    d1_packages = d1.app_list()

    with open(log, "a+", encoding="utf8") as f:
        for root, dirs, files in os.walk(apk_dir):
            for file in files:
                if file.endswith(".apk") or file.endswith(".xapk"):
                    print("apk " + str(index))
                    index += 1
                    filePath = os.path.join(root, file)

                    try:
                        packageName, mainActivity = getPackageByApk(filePath)
                        if packageName in d1_packages:
                            d1.app_stop(packageName)
                            d1.app_uninstall(packageName)
                            print("uninstall " + packageName)
                    except StopIteration:
                        print("time out " + file)
                        apks[file] = 3
                        f.write(file + delimiter + "3" + "\n")
                    except Exception:
                        print("fail other " + file)
                        apks[file] = 4
                        f.write(file + delimiter + "4" + "\n")


def pretty_json(obj):
    jobj = json.loads(obj) if (type(obj) is (str or bytes)) else obj
    try:
        return json.dumps(jobj, indent=4)
    except TypeError:
        return str(obj)


def pretty_print(*objs):
    for obj in objs:
        print(pretty_json(obj))


if __name__ == "__main__":
    saveDir = r"/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks"
    maxLen = 100

    apksDir = r"/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks"
    device1Id = "192.168.56.104"
    # uninstallApks_single(apksDir, device1Id)

    shorterFilename(saveDir)
