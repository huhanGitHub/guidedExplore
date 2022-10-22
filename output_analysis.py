import os
from itertools import chain, groupby
from pathlib import Path
from typing import Counter
from xml.etree import ElementTree

from cycler import add
from color_map import CLASS_MAP

import definitions
from dynamic_testing.hierachySolver import bounds2int
from utils.xml_helpers import *
from utils.group import Groups
from utils.path import create


def remove_repated(groups):
    # not work properly
    ans = [None]
    for group in sorted(groups, key=lambda g: g.act):
        if not group.is_same(ans[-1], 0.7):
            ans.append(group)
    return ans[1:]


def to_cls(e, g):
    cls = e.attrib.get("class")
    c = CLASS_MAP.get(cls)

    if c is None or c == "":
        return "unknown"
    else:
        return c


def print_statistics(data_dir=definitions.OUT_DIR):
    apps = (d for d in os.scandir(data_dir) if d.is_dir())
    group_nums = []
    unique_nums = []
    no_groups = 0
    has_groups = 0
    for app in apps:
        groups = Groups.from_folder(app.path, app.name)
        if len(groups) == 0:
            no_groups += 1
            continue
        else:
            has_groups += 1
            groups = [g for g in groups if g.is_legit()]
            lgroups = len(groups)
            group_nums.append(lgroups)
            if len(groups) > 0:
                lgroups = lgroups % 100
                unique_nums.append(lgroups)

        if len(groups) > 100:
            print(f"{app} has {len(groups)} groups")
    print(f"total pairs: {sum(group_nums)}")
    print(f"useful pairs: {sum(unique_nums)}")

    with open(definitions.FAIL_LOG_PATH) as f:
        failed = len(f.readlines())
        total = failed + has_groups + no_groups
        print(f"total number of apps: {total}")
        print(f"number of succeed apps: {has_groups}")
        print(f"apps has no pairs: {no_groups}")
        print(f"failed apps: {failed}")
    plot(unique_nums)


def plot(nums):
    import seaborn as sns

    sns.histplot(
        nums, binwidth=3, stat="count", legend=True
    ).set(title="Distribution of Number of Pairs from Collected App")
    import matplotlib.pyplot as plt

    plt.show()


def print_each_len():
    apps = [d for d in os.scandir(definitions.OUT_DIR) if d.is_dir()]
    for entry in apps:
        gs = Groups.from_folder(entry.path)
        if len(gs) > 40:
            print(entry.name)
            print(len(gs))


def test():
    groups = Groups.from_folder(
        os.scandir(os.path.join(definitions.DATA_DIR, "com.twitter.android"))
    )
    groups = [g for g in remove_repated(groups) if g.enough_nodes(5)]
    dest = os.path.join(definitions.DATA_DIR, "twitter.unique")
    for f in os.scandir(dest):
        os.remove(f.path)
    for g in groups:
        g.copy_to(dest)
        print(f"copy {g} to {dest}")


def move_to_unique():
    for entry in os.scandir(definitions.OUT_DIR):
        path = entry.path
        base = definitions._create(os.path.join(definitions.DATA_DIR, "unique"))
        gs = filter(lambda g: g.is_legit(), Groups.from_folder(path, entry.name))
        # gs = sorted(gs, key=lambda g: g.complexity())
        gs = {g.act: g for g in gs}.values()
        for g in gs:
            out = definitions._create(os.path.join(base, entry.name))
            # print(out)
            g.copy_to(out)


def move_to_unique2():
    gs = filter(lambda g: g.is_legit(), Groups.from_out_dir())
    gs = sorted(gs, key=lambda g: (g.act, g.id))
    prev = None
    out = lambda pkg: definitions._create(
        os.path.join(definitions.DATA_DIR, "unique2", pkg)
    )
    for g in gs:
        if not g.is_same(prev, 0.7):
            g.copy_to(out(g.pkg))


def class_distribution(groups):
    from collections import Counter

    cls = []
    for g in groups:
        for path in [g.txml, g.pxml]:
            root = ElementTree.parse(path)
            for e in root.iter():
                if e.attrib.get("package") == g.pkg:
                    cls.append(e.attrib.get("class"))
    return Counter(cls)


def test_diversity():
    def total_div(g):
        d = g.diversity()
        c = sum(g.xy_complexity())
        return min(d[0], d[1]), c

    out = os.path.join(definitions.DATA_DIR, "unique")
    gs = sorted(
        (g for g in Groups.from_out_dir(out) if g.is_legit()),
        key=total_div,
        reverse=True,
    )
    i = 0
    for g in gs:
        out = create(os.path.join(definitions.DATA_DIR, "example", g.pkg))
        print(g)
        i += 1
        if i == 100:
            exit()
        g.copy_to(out)
        # g.draw(out, "leaf")


def move_by_class(
    src=os.path.join(definitions.DATA_DIR, "test-grouping1"),
    dst=os.path.join(definitions.DATA_DIR, "by_class"),
):
    classes_map = {}
    for g in Groups.from_out_dir(src):
        for node in chain(g.ttree(), g.ptree()):
            cls = node.attrib["class"].split(":")[0]
            if classes_map.get(cls) is None:
                classes_map[cls] = [g]
            else:
                classes_map[cls].append(g)

    def filte(g):
        pn, tn = g.node_num(only_child=True)
        return 3 <= pn <= 10, 3 <= tn <= 10

    for cls, gs in classes_map.items():
        gs = sorted(gs, key=filte)
        path = definitions._create(os.path.join(dst, cls))
        for g in gs:
            g.copy_to(path)


if __name__ == "__main__":
    print_statistics(definitions.DATA_DIR + "/unique")
    print_statistics()
    # print_statistics(os.path.join(definitions.DATA_DIR, "sample"))
    # move_to_unique()
    move_by_class()
