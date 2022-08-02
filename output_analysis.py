import os
import re
import shutil
from itertools import chain, groupby, pairwise
from pathlib import Path
from xml.etree import ElementTree

from pyaxmlparser import APK

import definitions
from dynamic_testing.hierachySolver import bounds2int
from utils.xml_helpers import is_same_activity, xml_complexity, remove_sysui, exits_keyboard
from utils.path import basename_no_ext


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
    filter_sys_ui = is_attr_nq("package", "com.android.systemui")

    elements = tree.iter()

    # elements = tree.findall('.//node')
    elements = filter(filter_sys_ui, elements)
    return elements


def clickable_bounds(tree: ElementTree):
    pass_clickable = is_attr_eq("clickable", "true")
    elements = tree_to_list(tree)
    elements = filter(pass_clickable, elements)

    def to_bounds(element):
        return bounds2int(element.attrib.get("bounds"))

    bounds = map(to_bounds, elements)
    return bounds


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
    return [f for f in os.scandir(folder) if f.name.endswith(".xml")]


def _get_all_xmls():
    paths = os.scandir(definitions.OUT_DIR)
    xmls = sorted(
        [xml for path in paths if path.is_dir() for xml in _xmls(path)],
        key=lambda e: e.name,
    )
    return xmls


def act_name(f):
    if type(f) is os.DirEntry:
        f = f.name
    return f.split("_")[2]


def check_repeated(xmls, remove=False):
    fs = [f.path for f in xmls if "phone" in f.name]
    c = 0
    cpx = 0
    for i in range(0, len(fs) - 1):
        f1 = fs[i]
        f2 = fs[i - 1]
        # for (f1, f2) in pairwise(fs):
        s1 = Path(f1).read_text()
        s2 = Path(f2).read_text()
        if xml_complexity(f1) < 10:
            cpx += 1
            c += 1
            continue
        if is_same_activity(s1, s2, 0.9):
            c += 1
    print(f"""total: {len(fs)}
            too simple: {cpx}
            simple or repated: {c}, rate: {c / len(fs)},
            usable: {len(fs) - c}
            """
    )


def _get_app_count():
    paths = [f for f in os.scandir(definitions.OUT_DIR) if f.is_dir()]
    return len(paths)


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

    print(_get_app_count())
    print(len([i for i in a if i >= 15]))

    import seaborn as sns

    plot = sns.histplot(a)
    import matplotlib.pyplot as plt

    plt.show()


def _example_info():
    paths = os.scandir(definitions.OUT_DIR)
    xmls = [xml.path for path in paths if path.is_dir() for xml in _xmls(path)]

    def getl(root):
        return len(root.findall("*"))

    for xml in xmls:
        root = ElementTree.parse(xml).getroot()
        l = getl(root)
        if l != 2:
            print([(e.tag, e.attrib["package"]) for e in root.findall("*")])


def _show_failed():
    failed_apps = [f for f in open(definitions.FAIL_LOG_PATH).read().splitlines()]
    explored_apps = [f.name for f in os.scandir(definitions.OUT_DIR) if f.is_dir()]
    print(f"failed: {len(failed_apps)}, explored: {len(explored_apps)}")


def group_id(f):
    if type(f) is os.DirEntry:
        f = f.name
    return f.split('_')[0]


def group_act(f):
    if type(f) is os.DirEntry:
        f = basename_no_ext(f.name)
    return f.split('_')[2]

def bounds2p(b):
    (x1, y1, x2, y2) = bounds2int(b)
    return x1, y1
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    return x, y


def xml_to_bounds(f):
    tree = ElementTree.fromstring(Path(f).read_text())
    tree = remove_sysui(tree)
    nodes = [n for n in tree.iter('node') if len(n) == 0]  # leaf nodes
    bounds = [n.attrib.get('bounds') for n in nodes]
    bounds = [bounds2p(b)for b in bounds]
    return bounds


def bounds_complexity(bounds):
    xs = {i[0]: i for i in bounds}.keys()
    ys = {i[1]: i for i in bounds}.keys()
    return xs, ys


def group_complexity(group):
    p = xml_to_bounds(group.pxml.path)
    t = xml_to_bounds(group.txml.path)
    return bounds_complexity(p), bounds_complexity(t)


class Group():
    def __init__(self, group):
        self.id = group[0]
        self.files = list(group[1])
        self.act = group_act(self.files[0])
        for f in self.files:
            if f.name.endswith(".xml"):
                if "phone" in f.name:
                    self.pxml = f
                else:
                    self.txml = f
            else:
                if "phone" in f.name:
                    self.ppng = f
                else:
                    self.tpng = f

    def __gt__(self, other):
        (p1, t1) = group_complexity(self)
        (p2, t2) = group_complexity(other)
        if t1 == t2:
            return p1 > p2
        else:
            return t1 > t2

    def __repr__(self):
        return self.id + self.act

    def is_same(self, other):
        if other is None:
            return False
        if self.act != other.act:
            return False

        def content(entry):
            return Path(entry.path).read_text()
        try:
            return is_same_activity(content(self.txml), content(other.txml), 0.9) \
                or is_same_activity(content(self.pxml), content(other.pxml), 0.9)
        except:
            return False

    def copy_to(self, dest):
        for f in self.files:
            # dest = os.path.join(dest, f.name)
            shutil.copy(f.path, dest)

    def remove(self):
        for f in self.files:
            os.remove(f.path)

    def complexity(self):
        p = xml_to_bounds(self.pxml.path)
        t = xml_to_bounds(self.txml.path)
        return bounds_complexity(p), bounds_complexity(t)

    def complex_enough(self, target=5):
        ((px, py), (tx, ty)) = self.complexity()
        for b in [px, py, tx, ty]:
            if len(b) < target:
                return False
        return True


def remove_repated(groups):
    ans = [None]
    for group in sorted(groups, key=lambda g: g.act):
        if not group.is_same(ans[-1]):
            ans.append(group)
    return ans[1:]


def get_groups(files):
    groups = groupby(sorted(files, key=group_id), group_id)
    groups = [Group(g) for g in groups]
    return groups


def _get_all_files():
    paths = os.scandir(definitions.OUT_DIR)
    files = sorted(
        [f for path in paths if path.is_dir() for f in os.scandir(path)],
        key=lambda e: e.name,
    )
    return files


def to_cc10():
    a = 0
    def enough(g):
        return xml_complexity(g.pxml.path) >= 10 and xml_complexity(g.txml.path) >= 10
    for g in remove_repated(get_groups(_get_all_files())):
        if "Launcher" in g.act:
            continue
        if exits_keyboard(g.pxml.path) or exits_keyboard(g.txml.path):
            continue
        if enough(g):
            print(g)
            g.copy_to(os.path.join(definitions.DATA_DIR, "cc10"))
            a += 1
    print(a)


def to_c5():
    for g in remove_repated(get_groups(_get_all_files())):
        if "Launcher" in g.act:
            continue
        if exits_keyboard(g.pxml.path) or exits_keyboard(g.txml.path):
            continue
        if g.complex_enough():
            print(g)
            print(g.complexity())
            g.copy_to(os.path.join(definitions.DATA_DIR, "c5"))


def to_c10():
    for g in remove_repated(get_groups(_get_all_files())):
        if "Launcher" in g.act:
            continue
        if exits_keyboard(g.pxml.path) or exits_keyboard(g.txml.path):
            continue
        if g.complex_enough(10):
            print(g)
            print(g.complexity())
            g.copy_to(os.path.join(definitions.DATA_DIR, "c10"))


def only_phones():
    path = os.path.join(definitions.DATA_DIR, "compare", "click")
    n = 0
    for folder in filter(lambda e: e.is_dir(), os.scandir(path)):
        for g in get_groups(os.scandir(folder)):
            n += 1

    print(n)


if __name__ == "__main__":
    only_phones()
