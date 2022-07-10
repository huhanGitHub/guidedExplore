import os
import re
# import xml.etree as etree
from xml.etree import ElementTree
from pathlib import Path
from pyaxmlparser import APK
from utils.xml_helpers import pure_root


import definitions
# from util import getActivityPackage, installApk
from dynamic_testing.hierachySolver import bounds2int


def is_attr_nq(attr_name, expect_value):
    def func(element):
        value = element.attrib.get(attr_name)
        return value is not None and value != expect_value
    return func


def is_attr_eq(attr_name, expect_value):
    def func(element: ElementTree.Element):
        value = element.attrib.get(attr_name)
        return value is not None and value == expect_value
    return func


def tree_to_list(tree: ElementTree):
    filter_sys_ui = is_attr_nq('package', 'com.android.systemui')

    elements = tree.iter()

    # elements = tree.findall('.//node')
    elements = filter(filter_sys_ui, elements)
    return elements


def clickable_bounds(tree: ElementTree):
    pass_clickable = is_attr_eq('clickable', 'true')
    elements = tree_to_list(tree)
    elements = filter(pass_clickable, elements)

    def to_bounds(element):
        return bounds2int(element.attrib.get('bounds'))
    bounds = map(to_bounds, elements)
    return bounds


def is_same_activity(xml1: str, xml2: str):
    bounds1 = re.findall(r'\[.*\]', xml1)
    bounds2 = re.findall(r'\[.*\]', xml2)
    count = 0
    for (a, b) in zip(bounds1, bounds2):
        if a == b:
            count += 1
    rate = count / len(bounds1)
    print(f'similar rate: {rate}')
    return rate > 0.75


def xml_complexity(xml_path, package_name=None):
    s = Path(xml_path).read_text()
    t = ElementTree.fromstring(s)
    lst = tree_to_list(t)
    if package_name is not None:
        filter_sys_ui = is_attr_eq('package', package_name)
        lst = filter(filter_sys_ui, lst)
    length = sum(1 for _ in lst)
    return length


def _apk_paths(dir=definitions.APK_DIR):
    apks = sorted(os.listdir(dir))
    apks = map(lambda x: os.path.join(dir, x), apks)
    apks = [f for f in apks if os.path.splitext(f)[1] == ".apk"]
    return apks


def _out_paths():
    d = definitions.OUT_DIR
    apks = os.listdir(d)
    apks = map(lambda x: os.path.join(d, x), apks)
    return apks


def _xmls(folder):
    return [f for f in os.scandir(folder) if f.name.endswith('.xml')]


def tmp():
    outpus = {}

    def append(p, e):
        if outpus.get(p) is None:
            outpus[p] = [e]
        else:
            outpus[p].append(e)

    # apks = _out_paths()
    for apk in os.listdir(definitions.OUT_DIR):
        package_name = apk
        apk = os.path.join(definitions.OUT_DIR, apk)
        xmls = _xmls(apk)
        for xml in xmls:
            # xml = os.path.join(apk, xml)
            c = xml_complexity(xml, package_name)
            append(package_name, c)

    a = []
    for i in outpus.values():
        a.extend(i)

    print(len([i for i in a if i >= 10]))
    exit(0)

    import seaborn as sns
    plot = sns.histplot(a)
    import matplotlib. pyplot as plt
    plt.show()


if __name__ == '__main__':
    paths = os.scandir(definitions.OUT_DIR)
    xmls = [xml.path for path in paths if path.is_dir() for xml in _xmls(path)]

    def getl(root):
        return len(root.findall('*'))

    for xml in xmls:
        root = ElementTree.parse(xml).getroot()
        l = getl(root)
        if l != 2:
            print([(e.tag, e.attrib['package']) for e in root.findall("*")])
