import os
import time
import random
import subprocess

import definitions


# https://github.com/EFForg/rs-google-play/blob/master/gpapi/device.properties
x86_tablet = "cloudbook"
arm_tablet = "sailfish"


# https://github.com/EFForg/apkeep/blob/master/USAGE-google-play.md
def download(apk_id, outdir, device):
    subprocess.run(
        f"apkeep -a {apk_id} -d google-play -o device={device},split_apk=false -u 'guiautomation1@gmail.com' -p 'Qsc,./136' {outdir}",
        shell=True,
    )


def downloaded_apks():
    downloaded_apks = [
        f.name.removesuffix(".apk")
        for f in os.scandir(definitions.APK_DIR)
        if f.name.endswith(".apk")
    ]
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
            time.sleep(10)


if __name__ == "__main__":
    download_with_apkeep()
