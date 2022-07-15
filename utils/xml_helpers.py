import re
from pathlib import Path
from xml.etree import ElementTree


def bounds2int(bounds):
    bounds = bounds.replace("][", ",")
    bounds = bounds[1:-1]
    bounds = [int(i) for i in bounds.split(",")]
    return bounds


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
    root.remove(node)
    return root


def pure_root(root: ElementTree.Element, pkg_name: str=None):
    if pkg_name is None:
        return remove_sysui(root)

    node = root.find(f"./node[@package='{pkg_name}']")
    tree = ElementTree.ElementTree()
    tree._setroot(node)
    # tree.write('test.xml', encoding='unicode')
    return tree


def tree_to_list(tree: ElementTree):
    filter_sys_ui = is_attr_nq('package', 'com.android.systemui')

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


def exits_syserr(root: ElementTree.Element):
    """
    check system prompt with title like '...keeps stopping'
    """
    ans = root.find("./node[@package='android']")
    return ans is not None


def exits_keyboard(root: ElementTree.Element):
    ans = root.find("./node[@package='com.android.inputmethod.latin']")
    return ans is not None


def _test():
    path = 'data/outputs/com.alltrails.alltrails/1656998093_tablet_CreateListActivity.xml'
    root = ElementTree.parse(path).getroot()
    print(exits_keyboard(root))


if __name__ == '__main__':
    _test()
