import os
import definitions
import time
import random
import subprocess


# https://github.com/EFForg/rs-google-play/blob/master/gpapi/device.properties
x86_tablet = "cloudbook"
arm_tablet = "sailfish"


# https://github.com/EFForg/apkeep/blob/master/USAGE-google-play.md
def download(apk_id, outdir, device):
    subprocess.run(
        f"apkeep -a {apk_id} -d google-play -o device={device},split_apk=false -u 'guiautomation1@gmail.com' -p 'Qsc,./136' {outdir}",
        shell=True,
    )


def explored_apks():
    explored_apps = [f.name for f in os.scandir(definitions.OUT_DIR) if f.is_dir()]
    failed_apps = [f for f in open(definitions.FAIL_LOG_PATH).read().splitlines()]
    explored = set(explored_apps).union(set(failed_apps))
    return explored


def downloaded_apks():
    downloaded_apks = set(
        [
            f.name.removesuffix(".apk")
            for f in os.scandir(definitions.APK_DIR)
            if f.name.endswith(".apk")
        ]
    ).union(explored_apks())
    return downloaded_apks


def download_with_apkeep():
    with open("apps.json", "r") as f:
        # apps = [line.split("'")[1] for line in f.readlines() if "appId" in line]
        apps = [l.strip() for l in f.readlines()]
        downloaded = downloaded_apks()
        print(f"total: {len(apps)}, downloaded: {len(downloaded)}")
        apps = [a for a in apps if a not in downloaded]
        while len(apps) > 0:
            app = random.choice(list(apps))
            download(app, definitions.APK_DIR, x86_tablet)
            apps = [a for a in apps if a not in downloaded_apks()]
            time.sleep(30)


if __name__ == "__main__":
    download_with_apkeep()
