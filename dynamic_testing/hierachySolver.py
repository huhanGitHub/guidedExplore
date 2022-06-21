import xml.etree.ElementTree as ET

import uiautomator2.exceptions
import subprocess

viewList = ['android.widget.TextView', 'android.widget.ImageView', 'android.widget.Button']
removeView = ['']
textViewList = ['android.widget.TextView']
middleTexts = ['search']


def nodeCompare(node1, node2):
    text1 = node1.attrib.get('text', None)
    text2 = node2.attrib.get('text', None)
    resourceId1 = node1.attrib.get('resourceId', None)
    resourceId2 = node2.attrib.get('resourceId', None)
    description1 = node1.attrib.get('description', None)
    description2 = node2.attrib.get('description', None)

    count = 0
    if text1 == text2:
        count += 1
    if resourceId1 == resourceId2:
        count += 1
    if description1 == description2:
        count += 1

    if count >= 2:
        return True
    else:
        return False


def pairTextview(phoneViews, tabletViews):
    pairs = []
    for textview1 in phoneViews:
        text1 = textview1.attrib.get('text', None)
        for textview2 in tabletViews:
            text2 = textview2.attrib.get('text', None)
            if text1 == text2:
                pair = [textview1, textview2, text1]
                pairs.append(pair)
                break

    if len(pairs) <= 0:
        return None, None, None

    # select possible top tablayout texts according to Y axis less than 200
    top = []
    # select possible bottom navigation texts according to the Y axis more than 1700
    bottom = []
    middle = []
    for i in pairs:
        view = i[0]
        bounds = view.attrib.get('bounds')
        bounds = bounds2int(bounds)
        bounds2 = bounds2int(i[1].attrib.get('bounds'))
        text = view.attrib.get('text').lower()
        y1 = bounds[1]
        y2 = bounds[3]
        if y2 < 300:
            hasmiddle = False
            for j in middleTexts:
                if j in text:
                    hasmiddle = True
            if not hasmiddle:
                top.append([bounds, bounds2, i[-1]])
                continue
        elif y1 > 1700:
            bottom.append([bounds, bounds2, i[-1]])
            continue

        middle.append([bounds, bounds2, i[-1]])

    return top, bottom, middle


def bounds2int(bounds):
    bounds = bounds.replace('][', ',')
    bounds = bounds[1:-1]
    bounds = [int(i) for i in bounds.split(',')]
    return bounds


def hierachySolver(xml1, xml2):
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()

    tree2 = ET.ElementTree(ET.fromstring(xml2))
    root2 = tree2.getroot()

    # find all textviews in two xmls
    phoneViews = []
    tabletViews = []
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in textViewList:
            phoneViews.append(child)

    for child in root2.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in textViewList:
            tabletViews.append(child)

    if len(phoneViews) <= 0:
        return None

    top, bottom, middle = pairTextview(phoneViews, tabletViews)
    if top is None and bottom is None and middle is None:
        return None

    clickBounds = []
    if len(top) != 0:
        clickBounds.extend(top)
    if len(bottom) != 0:
        clickBounds.extend(bottom)
    if len(middle) != 0:
        if len(middle) >= 5:
            print('too many click points, truncate top10')
            middle = middle[:5]
        clickBounds.extend(middle)
    return clickBounds


def click_points_Solver(xml1):
    # find all leaf node in the xml
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()
    leaves = find_leaves(root1)

    ret_bounds = []
    for leaf in leaves:
        bounds = leaf.attrib.get('bounds')
        bounds = bounds2int(bounds)
        ret_bounds.append(bounds)

    return ret_bounds


def find_leaves(root1):
    # find all leaf node in the xml
    leaves = []

    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if len(child) == 0:
            package = child.attrib.get('package')
            if 'systemui' not in package:
                leaves.append(child)

    return leaves



def full_UI_click_test(sess, xml, cmd):
    leaves = click_points_Solver(xml)
    crash = []

    for leaf in leaves:
        bounds = leaf.attrib.get('bounds')
        bounds = bounds2int(bounds)
        try:
            sess.click((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
            sess.sleep(1)
            p = subprocess.run(cmd, shell=True, timeout=8)
        except subprocess.TimeoutExpired as e:
            print('cmd timeout')
            print(str(e))
            crash.append(leaf.attrib)
            return crash
        # except uiautomator2.exceptions.SessionBrokenError as e:
        #     print(str(e))
        #     crash.append(leaf)
    return crash

def text_compare(t1, t2):
    """
    Compare two text strings
    :param t1: text one
    :param t2: text two
    :return:
        True if a match
    """
    if not t1 and not t2:
        return True
    if t1 == '*' or t2 == '*':
        return True
    return (t1 or '').strip() == (t2 or '').strip()


def xml_compare(x1, x2, excludes=None, diff_items = 0):
    """
    Compares two xml etrees
    :param x1: the first tree
    :param x2: the second tree
    :param excludes: list of string of attributes to exclude from comparison
    :return:
        True if both files match
    """

    if excludes is None:
        excludes = []
    if x1.tag != x2.tag:
        # print('Tags do not match: %s and %s' % (x1.tag, x2.tag))
        diff_items += 1
        return False
    for name, value in x1.attrib.items():
        if not name in excludes:
            if x2.attrib.get(name) != value:
                # print('Attributes do not match: %s=%r, %s=%r'
                #                   % (name, value, name, x2.attrib.get(name)))
                diff_items += 1
                return False
    for name in x2.attrib.keys():
        if not name in excludes:
            if name not in x1.attrib:
                # print('x2 has an attribute x1 is missing: %s'
                #                   % name)
                diff_items += 1
                return False
    if not text_compare(x1.text, x2.text):
        # print('text: %r != %r' % (x1.text, x2.text))
        diff_items += 1
        return False
    if not text_compare(x1.tail, x2.tail):
        # print('tail: %r != %r' % (x1.tail, x2.tail))
        diff_items += 1
        return False
    cl1 = x1.getchildren()
    cl2 = x2.getchildren()
    if len(cl1) != len(cl2):
        # print('children length differs, %i != %i'
        #                   % (len(cl1), len(cl2)))
        diff_items += 1
        return False
    i = 0
    for c1, c2 in zip(cl1, cl2):
        i += 1
        if not c1.tag in excludes:
            if not xml_compare(c1, c2, excludes):
                # print('children %i do not match: %s'
                #                   % (i, c1.tag))
                return False
    return True


def GUI_state_change(xml1, xml2, max_diff_items=3):
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()
    # leaves1 = find_leaves(tree1)
    tree2 = ET.ElementTree(ET.fromstring(xml2))
    root2 = tree2.getroot()
    # leaves2 = find_leaves(tree2)

    diff_items = xml_compare(root1, root2)

    if diff_items:
        return False
    return True
