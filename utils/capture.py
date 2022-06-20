import definitions
import os


def capture(device, save_dir=definitions.APK_DIR):
    d_current = device.app_current()
    package = d_current["package"]
    activity = d_current["activity"]
    xml = device.dump_hierarchy()
    img = device.screenshot()

    def getPath(devicetype, filetype):
        return os.path.join(
            save_dir, f"{package}_{activity}_{devicetype}.{filetype}"
        )


def saveXmlScreen(saveDir, xml1, xml2, img1, img2, activity_name, package_name):
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
