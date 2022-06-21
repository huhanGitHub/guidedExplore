from utils.util import *
import xml.etree.ElementTree as ET
from dynamic_testing.hierachySolver import bounds2int

grantPermissinActivityFieldList = ['grantpermissions', 'grantpermission']
dialogList = ['android.widget.TextView', 'android.widget.Button']
yesFields = ['allow', 'yes', 'allow only while using the app', 'once', 'while using the app', 'only this time',
             'allow all the time', 'accept', 'accept & continue', 'later']
noFields = ['deny', 'no']
dialogField = ['ok', 'got it', 'allow', 'yes', 'always', 'cancel', 'continue', 'exit',
               'allow only while using the app', 'once',  'while using the app', 'only this time', 'allow all the time',
               'accept', 'accept & continue', 'later']
framelayoutList = ['android.widget.FrameLayout']
dialogNameField = ['dialog']


# com.android.packageinstaller.permission.ui.GrantPermissionsActivity deny allow
def grantPermissinActivityDetector(d):
    status = False
    d_activity, d_package, d_launcher = getActivityPackage(d)
    d_activity = str(d_activity).lower()
    for filed in grantPermissinActivityFieldList:
        if filed in d_activity:
            status = True
            break
    xml1 = d.dump_hierarchy(compressed=True)
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()
    # find all textviews in two xml
    textViews = []
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in dialogList:
            textViews.append(child)

    yesStatus = False
    noStatus = False
    for textview in textViews:
        text = textview.attrib.get('text', None)
        text = text.lower()
        if text in yesFields:
            yesStatus = True
        elif text in noFields:
            noStatus = True

    if yesStatus and noStatus:
        status = True

    # check dialog in framelayout
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in framelayoutList:
            for widget in child.iter():
                className = widget.attrib.get('class', None)
                if className is None:
                    continue
                text = widget.attrib.get('text')
                text = text.lower()
                if text in dialogField:
                    bounds = widget.attrib.get('bounds')
                    bounds = bounds2int(bounds)
                    d.click((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
                    print('solve dialog')

    # check dialog by fields
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in framelayoutList:
            resourceId = child.attrib.get('resource-id')
            if resourceId is None or resourceId == '':
                continue
            tag = False
            for i in dialogNameField:
                if i in resourceId:
                    tag = True
                    break
            if not tag:
                continue

            for widget in child.iter():
                className = widget.attrib.get('class', None)
                if className is None:
                    continue
                if className == 'android.widget.Button':
                    clickable = widget.attrib.get('clickable', False)
                    if not clickable:
                        continue
                    bounds = widget.attrib.get('bounds')
                    bounds = bounds2int(bounds)
                    d.click((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
                    print('solve dialog')

    return status


def grantPermissinActivityTasker(d):
    xml1 = d.dump_hierarchy(compressed=True)
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()
    # find all textviews in two xml
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in dialogList:
            ori_text = child.attrib.get('text', None)
            text = ori_text.lower()
            if text in yesFields:
                bounds = child.attrib.get('bounds')
                bounds = bounds2int(bounds)
                if bounds[1] >= 200 and bounds[3] <= 1600:
                    clickPointx = (bounds[0] + bounds[2]) / 2
                    clickPointy = (bounds[1] + bounds[3]) / 2
                    # tab: 2000 * 1200
                    # phone: 1080 * 2240
                    d.click(clickPointx, clickPointy)
                    # d(text=ori_text).click()
                    print('solve grant permission activity')


def dialogSolver(d):
    index = 0
    while grantPermissinActivityDetector(d):
        if index > 8:
            print('xml bounds error, click back')
            d.press('back')
            break
        grantPermissinActivityTasker(d)
        index += 1

    d.sleep(3)