import definitions
from utils.xml_helpers import bounds2int,path2tree
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
        return ElementTree.Element("node", {"class":"my.group",
            "bounds":f"{merge_elements(g)}"})
    else:
        return g


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


def _split_element(element):
    assert len(element) != 0, "spliting a leaf node"
    groups = []
    temp = []
    for child in element:
        if len(child) == 0:
            temp.append(child)
        else:
            if len(temp) != 0:
                groups.append(deepcopy(temp))
                temp = []
            groups.append(child)

    if len(temp) != 0:
        groups.append(temp)
    groups = map(list2element, groups)
    groups = filter(too_small, groups)
    groups = filter(lambda e: e.attrib.get("package") != "com.android.systemui",groups)
    return groups

def group_elements(tree):
    def str_g(g):
        if type(g) is list:
            return f"L: {len(g)}"
        else:
            return f"E: {g.tag, g.attrib.get('class'), g.attrib.get('bounds')}"

    def print_q(q):
        for i, g in enumerate(q):
            print(i, str_g(g)) 
        print()

    queue = [tree]
    ans = []
    while len(queue) + len(ans) <= 4:
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
                queue.extend(_split_element(e))
        except AssertionError:
            # my.group
            ans.append(e)
        queue = sorted(queue, key=area, reverse=True)
        # queue = sorted(queue, key=area)
    return ans + queue


def _test():
    out = os.path.join(definitions.DATA_DIR, "test")
    for g in Groups.from_folder(os.path.join(definitions.DATA_DIR, "example"))[:10]:
        # if g.id != "1658671534":
        #     continue
        pes = group_elements(g.ptree())
        tes = group_elements(g.ttree())
        g.copy_to(out)
        g.draw(out, [pes, tes])


def _one():
    path = "/home/di/Documents/FIT4441/guidedExplore/data/test/1658671579_phone_TopLevelActivity.xml"
    tree = path2tree(path)
    group_elements(tree)


if __name__ == "__main__":
    _test()
    # _one()


