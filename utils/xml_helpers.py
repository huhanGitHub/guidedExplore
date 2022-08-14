import os
import re
from pathlib import Path
from xml.etree import ElementTree


def path2tree(xml_path):
    if type(xml_path) is os.DirEntry:
        xml_path = xml_path.path
    s = Path(xml_path).read_text()
    t = ElementTree.fromstring(s)
    return t


def classes(tree, pkg_name):
    return set(e.attrib.get("class") for e in tree.findall(f".//node[@package='{pkg_name}']"))


def bounds2int(bounds: str):
    bounds = bounds.replace("][", ",")
    bounds = bounds[1:-1]
    bounds = [int(i) for i in bounds.split(",")]
    return bounds


def bounds2p(b, center=False):
    (x1, y1, x2, y2) = bounds2int(b)
    if center:
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return x, y
    else:
        return x1, y1


def tree2list(tree, pkg_name):
    return (e for e in tree.findall(f".//node[@package='{pkg_name}']"))

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


def remove_sysui(root: ElementTree.Element):
    node = root.find("./node[@package='com.android.systemui']")
    if node is not None:
        root.remove(node)
    return root


def purge_root(root: ElementTree.Element, pkg_name=None):
    if pkg_name is None:
        return remove_sysui(root)
    else:
        node = root.find(f"./node[@package='{pkg_name}']")
        tree = ElementTree.ElementTree()
        tree._setroot(node)
        return tree


def tree_to_list(tree: ElementTree):
    filter_sys_ui = is_attr_nq("package", "com.android.systemui")

    elements = tree.iter()

    # elements = tree.findall('.//node')
    elements = filter(filter_sys_ui, elements)
    return elements


def clickable_bounds(tree):
    """
    tree: ElementTree or str
    """
    if type(tree) is str:
        tree = ElementTree.fromstring(tree)

    pass_clickable = is_attr_eq("clickable", "true")
    elements = tree_to_list(tree)
    # elements = filter(pass_clickable, elements)

    def to_bounds(element):
        return bounds2int(element.attrib.get("bounds"))

    bounds = map(to_bounds, elements)
    return bounds


def is_same_activity(xml1: str, xml2: str, threshold=None):
    bounds1 = re.findall(r"\[.*\]", xml1)
    bounds2 = re.findall(r"\[.*\]", xml2)
    if threshold is None:
        for (a, b) in zip(bounds1, bounds2):
            if a != b:
                return False
        return True
    else:
        count = sum([1 for (a, b) in zip(bounds1, bounds2) if a == b])
        rate = count / len(bounds1) if len(bounds1) != 0 else 0
        return rate > threshold


def node_num(xml_path, package_name=None):
    s = Path(xml_path).read_text()
    t = ElementTree.fromstring(s)
    lst = tree_to_list(t)
    if package_name is not None:
        filter_sys_ui = is_attr_eq("package", package_name)
        lst = filter(filter_sys_ui, lst)
    length = sum(1 for _ in lst)
    return length


def exits_syserr(root: ElementTree.Element):
    """
    check system prompt with title like '...keeps stopping'
    """
    ans = root.find("./node[@package='android']")
    return ans is not None


def exits_keyboard(root):
    if type(root) is str:
        root = ElementTree.parse(root).getroot()

    samboard = "com.samsung.android.honeyboard"
    gboard = "com.google.android.inputmethod.latin"
    board = "com.android.inputmethod.latin"
    ans = root.find(f"./node[@package='{gboard}']")
    ans = ans is not None or root.find(f"./node[@package='{board}']")
    return ans is not None


def find(tree, pairs, ne_pairs={}):
    def is_target(e):
        for key, value in pairs.items():
            if value.lower() not in e.attrib.get(key).lower():
                return False
        for key, value in ne_pairs.items():
            if value.lower() in e.attrib.get(key).lower():
                return False
        return True

    if type(tree) is str:
        tree = ElementTree.fromstring(tree)

    for e in tree.iter("node"):
        if is_target(e):
            return e
    return None


def get_pos_from_element(e: ElementTree.Element):
    if e is None:
        return None
    (x1, y1, x2, y2) = bounds2int(e.attrib.get("bounds"))
    return (x1 + x2) / 2, (y1 + y2) / 2


def find_google_login(xml: str):
    def is_google_btn(e):
        return (
            "google" in e.attrib.get("text").lower()
            and e.attrib.get("clickable") == "true"
        )

    root = ElementTree.fromstring(xml)
    es = [e for e in root.iter("node") if is_google_btn(e)]
    if len(es) > 0:
        (x1, y1, x2, y2) = bounds2int(es[0].attrib.get("bounds"))
        return (x1 + x2) / 2, (y1 + y2) / 2
    else:
        return None


def find_x_login(xml: str, x):
    def is_login_btn(e):
        return (
            x.lower() in e.attrib.get("text").lower()
            and e.attrib.get("clickable") == "true"
        )

    root = ElementTree.fromstring(xml)
    es = [e for e in root.iter("node") if is_login_btn(e)]
    if len(es) > 0:
        (x1, y1, x2, y2) = bounds2int(es[0].attrib.get("bounds"))
        return (x1 + x2) / 2, (y1 + y2) / 2
    else:
        return None


def click_if_find(d, pairs):
    xml = d.dump_hierarchy()
    pairs["clickable"] = "true"
    pos = get_pos_from_element(find(xml, pairs))
    if pos is not None:
        d.click(*pos)
        return True
    else:
        return False


def type_if_find(d, pairs, text):
    xml = d.dump_hierarchy()
    pairs["focusable"] = "true"
    pairs["clickable"] = "true"
    pairs["class"] = "Text"
    if pairs.get("text") is not None:
        pairs["resource-id"] = pairs.get("text")

    pos = get_pos_from_element(find(xml, pairs, {"class": "android.widget.EditText"}))
    if pos is not None:
        d.click(*pos)
        d.send_keys(text)


def xml_to_bounds(f):
    tree = ElementTree.fromstring(Path(f).read_text())
    tree = remove_sysui(tree)
    nodes = [n for n in tree.iter("node") if len(n) == 0]  # leaf nodes
    bounds = [n.attrib.get("bounds") for n in nodes]
    bounds = [bounds2p(b) for b in bounds]
    return bounds
