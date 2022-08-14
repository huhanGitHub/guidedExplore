import definitions
from utils.xml_helpers import bounds2int,path2tree, bounds2p
from xml.etree import ElementTree
import os
from utils.group import Groups
import definitions
from copy import deepcopy


def area(element):
    (a,b,c,d) = bounds2int(element.attrib["bounds"])
    return (d - b) * (c - a)

def too_small(element):
    (a,b,c,d) = bounds2int(element.attrib["bounds"])
    return (d - b) >= 20 and (c - a) >= 20

def list2element(g):
    if type(g) is list:
        if len(g) == 1:
            return g[0]
        else:
            return ElementTree.Element("node", {"class":"my.group",
                "bounds":f"{merge_elements(g)}"})
    elif type(g) is ElementTree.Element:
        return g
    else:
        raise RuntimeError(type(g))


def group_to_str(g):
    if type(g) is list:
        return f"L: {len(g)}"
    else:
        return f"E: {g.attrib.get('class')}"


def merge_elements(es):
    bs = (bounds2int(e.attrib["bounds"]) for e in es)
    x, y, a, b = next(bs)
    for (x1, y1 , x2, y2) in bs:
        x = x1 if x1 < x else x
        y = y1 if y1 < y else y
        a = x2 if x2 > a else a
        b = y2 if y2 > b else b
    return f"[{x},{y}][{a},{b}]"


def _group_leaves(elements):
    groups = []
    temp = []
    for e in elements:
        if len(temp) == 0:
            temp.append(e)
        else:
            (x, y) = bounds2p(temp[-1].attrib["bounds"], center=True)
            _x, _y = bounds2p(e.attrib["bounds"], center=True)
            if abs(x - _x) <= 10 or abs(_y - y) <= 10:
                temp.append(e)
            else:
                groups.append(list2element(temp))
                temp = [e]
    if len(temp) != 0:
        groups.append(list2element(temp))
    return groups


def _squeeze_single(element):
    while True:
        if len(element) == 1:
            element = element.find("./")
            print("squeezed: ", element.attrib["class"], element.attrib["bounds"])
        else:
            return element

def _squeeze_tree(tree):
    """
    replace elements with one child to its child
    """
    tree = _squeeze_single(tree)
    queue = [tree]
    while len(queue) != 0:
        e = queue.pop()
        children = list(e.findall("./"))
        for child in children:
            e.remove(child)
            after = _squeeze_single(child)
            # after.attrib["bounds"] = child.attrib["bounds"]
            e.append(after)
        for child in e:
            if len(child) != 0:
                queue.append(child)
    return tree

def _split_element(element):
    assert len(element) != 0, "spliting a leaf node"
    print("spliting: ", element.attrib["class"], element.attrib["bounds"])
    groups = []
    temp = []
    for child in element:
        if len(child) == 0:
            temp.append(child)
        else:
            if len(temp) != 0:
                # groups.append(deepcopy(temp))
                groups.extend(_group_leaves(temp))
                temp = []
            groups.append(child)

    if len(temp) != 0:
        groups.extend(_group_leaves(temp))
        # groups.append(temp)
    groups = map(list2element, groups)
    groups = filter(too_small, groups)
    return groups

def group_elements(tree, pkg):
    def str_g(g):
        if type(g) is list:
            return f"L: {len(g)}"
        else:
            return f"E: {g.tag, g.attrib.get('class'), g.attrib.get('bounds')}"

    def print_q(q):
        for i, g in enumerate(q):
            print(i, str_g(g)) 
        print()

    tree = tree.find(f"./node[@package='{pkg}']")
    try:
        queue = _split_element(tree)
    except AssertionError:
        queue = [tree]
    queue = list(queue)
    ans = []
    print("start")
    print_q(queue)
    # pre: queue are groups, ans are grouped leaves
    while len(queue) + len(ans) <= 4:
        queue = sorted(queue, key=area, reverse=True)
        queue = list(filter(too_small, queue)
        print("filtered")
        print_q(queue)
        try:
            e = queue.pop(0)
        except IndexError:
            break
        # input("...")
        try:
            split = list(_split_element(e))
            if len(split) + len(queue) + len(ans) > 5:
                # if too much
                queue.append(e)
                break
            else:
                queue.extend(split)
        except AssertionError:
            # my.group
            ans.append(e)
        print("filtering")
        print_q(queue)
        # queue = sorted(queue, key=area)
    # end: queue are groups, ans are grouped leaves
    print("done:")
    print_q(ans +queue)
    return ans + queue


def _test():
    out = os.path.join(definitions.DATA_DIR, "test")
    for g in Groups.from_out_dir(os.path.join(definitions.DATA_DIR, "example")):
        # if g.pkg != "com.alltrails.alltrails":
            # continue
        pes = group_elements(_squeeze_tree(g.ptree()), g.pkg)
        tes = group_elements(_squeeze_tree(g.ttree()), g.pkg)
        g.copy_to(out)
        g.draw(out, [pes, tes])


def _one():
    path = "/home/di/Documents/FIT4441/guidedExplore/data/test/1658671579_phone_TopLevelActivity.xml"
    tree = path2tree(path)
    group_elements(tree)


if __name__ == "__main__":
    _test()
    # _one()


