import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

#OUT_DIR = os.path.join(ROOT_DIR, "results")
OUT_DIR = "results"
if not os.path.exists(OUT_DIR):
    print(f"Creating data output directory: {OUT_DIR}")
    os.mkdir(OUT_DIR)

APK_DIR = os.path.join(ROOT_DIR, "resources", "apks")
if not os.path.exists(APK_DIR):
    print(f"Creating apk directory: {APK_DIR}")
    os.mkdir(APK_DIR)


CSV_PATH = os.path.join(OUT_DIR, "results.csv")
TABLET_CSV_PATH = os.path.join(OUT_DIR, "tablet_results.csv")
# path for only using one device and changing resolution instead
CSV_PATH2 = os.path.join(OUT_DIR, "results2.csv")
# VM
CSV_VM = os.path.join(OUT_DIR, "results_vm.csv")

# get serial number by $>adb devices
PHONE_ID = "LMK420TSUKR8PVTG7P"
TABLET_ID = "R52RA0C2MFF"
VM_ID = "192.168.57.107:5555"
