from collections import Counter
import threading
from color_map import CLASS_MAP
import definitions
from utils.xml_helpers import bounds2int, bounds2p
from xml.etree import ElementTree
import os
from utils.group import Groups
import re


def is_one_of(target, subs):
    for s in subs:
        if s not in target:
            return False
    return True


def area(element):
    (a, b, c, d) = bounds2int(element.attrib["bounds"])
    return (d - b) * (c - a)


def big_enough(element):
    (a, b, c, d) = bounds2int(element.attrib["bounds"])
    return (d - b) >= 40 and (c - a) >= 40


def guess_class(group, x1, y1, x2, y2):
    if y1 == 48 and y2 < 200:
        print("a top bar:", [e.attrib.get("text") for e in group], x1, y1, x2, y2)
        return "topbar"

    classes = Counter(CLASS_MAP.get(e.attrib.get("class")) for e in group) + Counter(
        e.attrib.get("class") for e in group
    )
    most_cls = classes.most_common(1)[0][0]
    if most_cls is None or most_cls == "":
        most_cls = "my.group"
    return most_cls


def list2element(g):
    if type(g) is list:
        if len(g) == 1:
            return g[0]
        else:
            bounds = merge_bounds(g)
            (x1, y1, x2, y2) = bounds2int(bounds)
            ele = ElementTree.Element(
                "node", {"class": guess_class(g, x1, y1, x2, y2), "bounds": f"{bounds}"}
            )
            # WARN: cause group_elements endless loop
            # ele.extend(g)
            return ele
    elif type(g) is ElementTree.Element:
        return g
    else:
        raise RuntimeError(type(g))


def group_to_str(g):
    if type(g) is list:
        return f"L: {len(g)}"
    else:
        return f"E: {g.attrib.get('class')}"


def merge_bounds(es):
    bs = (bounds2int(e.attrib["bounds"]) for e in es)
    x, y, a, b = next(bs)
    for (x1, y1, x2, y2) in bs:
        x = x1 if x1 < x else x
        y = y1 if y1 < y else y
        a = x2 if x2 > a else a
        b = y2 if y2 > b else b
    return f"[{x},{y}][{a},{b}]"


def _squeeze_single(element):
    bounds = element.attrib.get("bounds")
    # recusively squeeze
    while True:
        if len(element) == 1:
            element = element.find("./")
        else:
            element.attrib["bounds"] = bounds
            return element


def _squeeze_tree(tree):
    """
    replace one-child elements to the child
    """
    tree = _squeeze_single(tree)
    queue = [tree]
    while len(queue) != 0:
        e = queue.pop()
        children = list(e.findall("./"))
        for child in children:
            e.remove(child)
            after = _squeeze_single(child)
            e.append(after)
        for child in e:
            if len(child) != 0:
                queue.append(child)
    return tree


def _group_by_position(elements):
    "group elements by bounds"
    groups = []
    similar_es = []
    for e in elements:
        if len(similar_es) == 0:
            similar_es.append(e)
        else:
            (x, y) = bounds2p(similar_es[-1].attrib["bounds"], center=True)
            _x, _y = bounds2p(e.attrib["bounds"], center=True)
            is_center_close = abs(x - _x) <= 10 or abs(_y - y) <= 10
            (x, y) = bounds2p(similar_es[-1].attrib["bounds"])
            _x, _y = bounds2p(e.attrib["bounds"])
            is_edge_close = abs(x - _x) <= 10 or abs(_y - y) <= 10
            if is_center_close or is_edge_close:
                similar_es.append(e)
            else:
                groups.append(list2element(similar_es))
                similar_es = [e]
    if len(similar_es) != 0:
        groups.append(list2element(similar_es))
    return groups


def _group_by_structure(element):
    assert len(element) != 0, "spliting a leaf node"
    groups = []
    mygroups = []
    for child in element:
        if len(child) == 0:
            mygroups.append(child)
        else:
            if len(mygroups) != 0:
                groups.extend(_group_by_position(mygroups))
                mygroups = []
            groups.append(child)

    if len(mygroups) != 0:
        groups.extend(_group_by_position(mygroups))
        # groups.append(temp)
    groups = map(list2element, groups)
    groups = filter(big_enough, groups)
    return list(groups)


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
        queue = _group_by_structure(tree)
    except AssertionError:
        queue = [tree]
    grouped = []
    # pre: queue are groups, ans are grouped leaves
    UPPER = 5
    while len(queue) + len(grouped) < UPPER - 1:
        queue = list(filter(big_enough, queue))
        try:
            e = max(queue, key=area)
            queue.remove(e)
        except ValueError:
            break
        try:
            split = list(_group_by_structure(e))
            if len(split) + len(queue) + len(grouped) > UPPER:
                # if too much
                split2 = _group_by_position(split)
                if len(split2) + len(queue) + len(grouped) > UPPER:
                    queue.append(e)
                else:
                    queue.extend(split2)
                break
            else:
                queue.extend(split)
        except AssertionError:
            grouped.append(e)
    res = grouped + queue
    print(">done")
    print_q(res)
    print("done<")
    return res


def _test():
    base = os.path.join(definitions.DATA_DIR, "test-grouping")

    if True:
        source = os.path.join(definitions.DATA_DIR, "example")
        groups = (g for g in Groups.from_out_dir(source) if g.is_legit())
    else:
        pkg = "aplicacion.tiempo"
        pkg = "air.com.myheritage.mobile"
        source = os.path.join(definitions.DATA_DIR, "example", pkg)
        groups = (g for g in Groups.from_folder(source, pkg) if g.is_legit())

    def _grouping_one(g):
        print(g)
        pes = group_elements(_squeeze_tree(g.ptree()), g.pkg)
        tes = group_elements(_squeeze_tree(g.ttree()), g.pkg)
        out = definitions._create(os.path.join(base, g.pkg))
        g.copy_to(out)
        g.draw(out, [pes, tes])

    threads = [
        threading.Thread(target=_grouping_one, args=[g]) for i, g in enumerate(groups)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    _test()
