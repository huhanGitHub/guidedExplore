import os
import re
import time
import random
import subprocess
import zipfile
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

import definitions


# https://github.com/EFForg/rs-google-play/blob/master/gpapi/device.properties
x86_tablet = "cloudbook"
arm_tablet = "sailfish"


# https://github.com/EFForg/apkeep/blob/master/USAGE-google-play.md
def download(apk_id, outdir, device):
    subprocess.run(f"apkeep -a {apk_id} -d google-play -o device={device},split_apk=false -u 'guiautomation1@gmail.com' -p 'Qsc,./136' {outdir}", shell=True)


def downloaded_apks():
    downloaded_apks = [f.name.removesuffix(".apk") for f in os.scandir(definitions.APK_DIR)
            if f.name.endswith(".apk") ]
    return downloaded_apks

def download_with_apkeep():
    with open('apps.json', 'r') as f:
        apps = [line.split("'")[1] for line in f.readlines() if 'appId' in line]
        print(f"total: {len(apps)}")
        apps = [a for a in apps if a not in downloaded_apks()]
        while len(apps) > 0:
            app = random.choice(list(apps))
            download(app, definitions.APK_DIR, x86_tablet)
            apps = [a for a in apps if a not in downloaded_apks()]
            time.sleep(30)


def searchByName_apkpure(app_name):
    # replace ' ' with '+'
    try:
        app_name = app_name.replace(' ', '+')
        server_addr = 'https://apkpure.com'
        url = 'https://apkpure.com/search?q=' + app_name + '&t=app'
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=headers)
        # search app
        get_html = urlopen(req).read()
        get_html = get_html.decode('utf-8')
        soup = BeautifulSoup(get_html, 'html.parser')
        apps = soup.find_all('a', {'title': re.compile(' APK$')})

        href = apps[0]['href']
        url2 = server_addr + href + '/versions'
        # print(full_href)

        # click first app, and go to its version page
        req2 = Request(url2, headers=headers)
        get_html2 = urlopen(req2).read()
        get_html2 = get_html2.decode('utf-8')
        soup2 = BeautifulSoup(get_html2, 'html.parser')
        ul = soup2.find('ul', {"class": "ver-wrap"})
        versions = ul.find_all('li')
        url3 = ''
        for index, version in enumerate(versions):
            xapk = version.find('span', {"class": "ver-item-t ver-xapk"})
            # download 'apk'
            if xapk is None:
                apk_link = version.find('a')['href']
                url3 = server_addr + apk_link
                break

        if url3 == '':
            print('no apk version, download xapk instead')
            apk_link = versions[0].find('a')['href']
            url3 = server_addr + apk_link
            download_link = xapk_downloader(url3, headers, server_addr)
        else:
            # find click download
            req3 = Request(url3, headers=headers)
            get_html3 = urlopen(req3).read()
            get_html3 = get_html3.decode('utf-8')
            soup3 = BeautifulSoup(get_html3, 'html.parser')
            download_link = soup3.find('a', {"id": "download_link"})['href']
    except Exception as e:
        print(str(e))
        return False

    return download_link


def url_downloader(url, app_name, save_dir):
    try:
        req = Request(url)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36')
        save_path = os.path.join(save_dir, app_name + '.zip')
        if os.path.exists(save_path):
            print(app_name + ' has been downloaded')
            return save_path
        response = urlopen(req).read()
        open(save_path, 'wb').write(response)
    except Exception as e:
        print(str(e))
        return False

    return save_path


def xapk_downloader(url3, headers, server_addr):
    req3 = Request(url3, headers=headers)
    get_html3 = urlopen(req3).read()
    get_html3 = get_html3.decode('utf-8')
    soup3 = BeautifulSoup(get_html3, 'html.parser')
    apk_link = soup3.find('a', text="Download XAPK")['href']

    url4= server_addr + apk_link
    # find click download
    req4 = Request(url4, headers=headers)
    get_html4 = urlopen(req4).read()
    get_html4 = get_html4.decode('utf-8')
    soup4 = BeautifulSoup(get_html4, 'html.parser')
    download_link = soup4.find('a', {"id": "download_link"})['href']
    return download_link


def zip_extractor(zip_path, save_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # get modified app name
        modified_app = zip_path[str(zip_path).rindex('/') + 1:-4]
        extracted_app = os.path.join(save_dir, modified_app)
        # remove .zip
        zip_ref.extractall(extracted_app)


def find_android_app(app_name, save_dir, extracted=True):
    url = searchByName_apkpure(app_name)
    if url is False:
        return False
    zip_path = url_downloader(url, app_name, save_dir)
    if zip_path is False:
        return False
    extracted_app_dir = save_dir[:-4] + 'extracted'
    if extracted:
        zip_extractor(zip_path, extracted_app_dir)
    return True


def batch_find_android_app(app_list, save_dir, extracted=True):
    apps = []
    with open(app_list, 'r', encoding='utf8') as f:
        apps = f.readlines()
        apps = [i.replace('\n', '') for i in apps]

    failed_app_path = r'/Users/hhuu0025/PycharmProjects/AISecurity/data/topAppleApps/failed_Android_apps2.txt'
    with open(failed_app_path, 'a', encoding='utf8') as f1:
        for index, app in enumerate(apps):
            status = find_android_app(app, save_dir, extracted=extracted)
            if not status:
                f1.write(app + '\n')
            print(str(status) + ' ' + app + ' ' + str(index))


if __name__ == '__main__':
    download_with_apkeep()
    app_name = 'Webex Meetings'
    save_dir = r'/Volumes/daneimiji/AndroidApps/topRatedApps/tempApk'
    # find_android_app(app_name, save_dir)
    # searchByName_apkpure(app_name)
    app_list = r'/Users/hhuu0025/PycharmProjects/AISecurity/data/topAppleApps/failed_Android_apps.txt'
    # batch_find_android_app(app_list, save_dir, extracted=False)
