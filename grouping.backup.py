import threading
from color_map import CLASS_MAP
import definitions
from utils.xml_helpers import bounds2int, bounds2p, bounds_of
from utils.device import Device
from xml.etree import ElementTree
import os
from utils.group import Groups


def big_enough(element):
    (a, b, c, d) = bounds2int(element.attrib["bounds"])
    return (d - b) >= 25 and (c - a) >= 25


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


def guess_class(group, x1, y1, x2, y2, type):
    if type == 'tablet':
        H = Device.TABLET_H
        W = Device.TABLET_W
    elif type == 'phone':
        H = Device.PHONE_H
        W = Device.PHONE_W

    if y2 < H * 0.2 and y1 == 48:
        return "TopBar"
    # elif y1 > H * 0.9:
        # return "BottomBar"

    allbounds = (bounds2int(e.attrib.get("bounds")) for e in group)
    classes = set(e.attrib.get("class").split(".")[-1] for e in group)
    x1s = set((b[0], b[1] - b[3]) for b in allbounds)
    y1s = set(b[1] for b in allbounds)
    if len(x1s) == 1:
        return "List"
    elif len(y1s) == 1:
        return "HorList"
    # search
    # top tab layout
    # list view
    # pic side info
    # big pic
    # side nav
    # bottom tab layout
    elif "tab" in classes:
        return "Tab"
    elif classes == set(["text"]):
        return "TextInfo"
    # icon + info
    elif classes == set(["text", "control"]):
        return "TextControl"
    elif "image" in classes:
        if classes == set(["text", "image"]):
            return "IconInfo"
    return ",".join(classes)


def list2element(g, device):
    if type(g) is list:
        if len(g) == 1:
            return g[0]
        else:
            bounds = merge_bounds(g)
            ele = ElementTree.Element(
                "node",
                {
                    "class": guess_class(g, *bounds2int(bounds), device),
                    "bounds": f"{bounds}",
                    "index": g[0].attrib["index"],
                },
            )
            return ele
    elif type(g) is ElementTree.Element:
        return g
    else:
        raise RuntimeError(type(g), " is not tree element")


def _group_by_position(elements, type):
    "group elements by bounds"
    groups = []
    buffer = []
    for e in elements:
        if len(buffer) == 0:
            buffer.append(e)
        else:
            (x, y) = bounds2p(buffer[-1].attrib["bounds"], center=True)
            _x, _y = bounds2p(e.attrib["bounds"], center=True)
            is_center_close = abs(x - _x) <= 10 or abs(_y - y) <= 10
            (x, y) = bounds2p(buffer[-1].attrib["bounds"])
            _x, _y = bounds2p(e.attrib["bounds"])
            is_edge_close = abs(x - _x) <= 10 or abs(_y - y) <= 10
            if is_center_close or is_edge_close:
                buffer.append(e)
            else:
                if len(buffer) != 0:
                    groups.append(list2element(buffer, type))
                    buffer = []
                buffer.append(e)
    if len(buffer) != 0:
        # TODO keep child while merging
        groups.append(list2element(buffer, type))
    return groups


def _group_by_pos_cls(elements, type, dir="hor"):
    "group elements by bounds"
    groups = []
    buffer = []
    for e in elements:
        if len(buffer) == 0:
            buffer.append(e)
        else:
            (ax1, ay1, ax2, ay2) = bounds_of(buffer[-1])
            (bx1, by1, bx2, by2) = bounds_of(e)

            def is_close(a, b):
                return abs(a - b) <= 10

            if dir == "hor":
                inrange1 = ay1 <= by1 < ay2
                inrange2 = ay1 < by2 <= ay2
                inrange3 = by1 <= ay1 < by2
                inrange4 = by1 < ay2 <= by2
                cmp_pos = inrange1 or inrange2 or inrange3 or inrange4
                cmp_cls = True
            else:
                center_ax = (ax1 + ax2) / 2
                center_bx = (bx1 + bx2) / 2
                is_center_close = is_close(center_ax, center_bx)
                is_edge_close = is_close(ax1, bx1) or is_close(ax2, bx2)
                cmp_pos = is_center_close or is_edge_close
                is_same_cls = buffer[-1].attrib["class"] == e.attrib["class"]
                cmp_cls = is_same_cls if dir != "hor" else True
            if cmp_cls and cmp_pos:
                buffer.append(e)
            else:
                if len(buffer) != 0:
                    groups.append(list2element(buffer, type))
                    buffer = []
                buffer.append(e)
    if len(buffer) != 0:
        groups.append(list2element(buffer, type))
    return groups


def _group_by_structure(element, type):
    assert len(element) != 0, "spliting a leaf node"
    ungrouped = []
    grouped = []
    buffer = []
    for child in element:
        if len(child) == 0:
            buffer.append(child)
        else:
            if len(buffer) != 0:
                grouped.extend(_group_by_position(buffer, type))
                buffer = []
            ungrouped.append(child)

    if len(buffer) != 0:
        grouped.extend(_group_by_position(buffer, type))

    def group_by_type(g):
        return list2element(g, type)
    grouped = list(map(group_by_type, grouped))
    return ungrouped, grouped


def group_elements(tree, pkg, type):
    # preprocess tree
    tree = tree.find(f"./node[@package='{pkg}']")
    for i, e in enumerate(tree.iter()):
        if len(e) == 1:
            e[0].attrib["bounds"] = e.attrib["bounds"]
        e.attrib["index"] = str(i)
        text_field = e.attrib.get("text")
        cls = CLASS_MAP.get(e.attrib.get("class"))
        if cls is not None and len(cls) > 0:
            e.attrib["class"] = cls
        else:
            if cls is None and len(text_field) > 0:
                e.attrib["class"] = "text"
            else:
                short = e.attrib["class"].split(".")[-1]
                e.attrib["class"] = short
                if "LinearLayout" == short and len(e) == 0:
                    (x1, y1, x2, y2) = bounds_of(e)
                    if (y2 - y1) / (x2 - x1) < 1.5:
                        e.attrib["class"] = "image"

    def print_g(g):
        for e in g:
            e = e.attrib
            print(f"{e['index']} {e['class']} {e['bounds']} {e.get('text')} {e.get('resource-id')}")

    queue = [tree]
    grouped = []
    while True:
        # print("===>>> grouped")
        # print_g(grouped)
        # input("next?")
        try:
            e = queue.pop(0)
        except IndexError:
            break
        try:
            ungrouped, groupedd = _group_by_structure(e, type)
            grouped.extend(groupedd)
            queue.extend(ungrouped)
        except AssertionError:
            grouped.append(e)
    assert len(queue) == 0
    res = grouped

    def by_index(e):
        return int(e.attrib["index"])

    res = filter(big_enough, res)
    res = sorted(res, key=by_index)
    res = _group_by_pos_cls(res, type, "hor")
    res = _group_by_pos_cls(res, type, "ver")

    # newtree = ElementTree.Element("node")
    # for e in pes:
    #     newtree.append(e)
    # ElementTree.indent(newtree)
    # ElementTree.dump(newtree)
    return res


def _test():
    base = definitions._create(os.path.join(definitions.DATA_DIR, "test-grouping2"))

    pkg = "cn.wps.moffice_eng"
    pkg = None
    if pkg is None:
        source = os.path.join(definitions.DATA_DIR, "sample")
        groups = (g for g in Groups.from_out_dir(source) if g.is_legit())
    else:
        source = os.path.join(definitions.DATA_DIR, "sample", pkg)
        groups = (g for g in Groups.from_folder(source, pkg) if g.is_legit())

    def _grouping_one(g):
        print(g)
        pt = g.ptree()
        pes = group_elements(pt, g.pkg, "phone")
        tt = g.ttree()
        tes = group_elements(tt, g.pkg, "tablet")
        out = definitions._create(os.path.join(base, g.pkg))
        g.copy_to(out)
        g.draw(out, [pes, tes])

    if PAL:
        threads = [
            threading.Thread(target=_grouping_one, args=[g])
            for i, g in enumerate(groups)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    else:
        for g in groups:
            # if g.id == "1663772752":
            _grouping_one(g)


if __name__ == "__main__":
    PAL = True
    _test()
