import os


def batch_decompile(apk_dir, save_dir, re_packaged_dir):
    for root, dirs, files in os.walk(apk_dir):
        for apk in files:
            if not str(apk).endswith('.apk'):
                continue
            apk_path = os.path.join(root, apk)
            app_save_dir = os.path.join(save_dir, apk)
            re_packaged_apk = os.path.join(re_packaged_dir, apk)
            if os.path.exists(app_save_dir) and os.path.exists(re_packaged_apk):
                print(apk + 'skip')
                continue
            unit_decpmpile(apk_path, app_save_dir)


# /Users/xxx/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/xxx/.android/debug.keystore /Users/xxx/PycharmProjects/uiautomator2/activityMining/re_apks/bilibili_v1.16.2_apkpure.com.apk

#  /Users/xxx/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks activityMining/apkSignedKey --ks-key-alias key0 --ks-pass pass:123456 --key-pass pass:123456 --v4-signing-enabled false  /Users/xxx/PycharmProjects/uiautomator2/activityMining/re_apks/youtube.apk

# /Users/xxx/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/xxx/.android/debug.keystore --ks-pass pass:android --key-pass pass:android  /Users/h
# xxx/PycharmProjects/uiautomator2/activityMining/re_apks/youtube.apk


def unit_decpmpile(apk_path, app_save_dir):
    print('Start apktool')
    cmd1 = 'apktool d ' + apk_path + ' -f -o ' + app_save_dir
    os.system(cmd1)


if __name__ == '__main__':

    apk_dir = r'../uiautomator2/apks'
    save_dir = r'../data/recompiled_apks'

    # batch_decompile(apk_dir, save_dir, re_packaged_dir)

    apk_path = r'data/apks/youtube.apk'
    app_save_path = r'data/recompiled_apks/youtube'
    unit_decpmpile(apk_path, app_save_path)

