import os
from itertools import groupby
from pathlib import Path
from xml.etree import ElementTree

import definitions
from dynamic_testing.hierachySolver import bounds2int
from utils.xml_helpers import *
from utils.group import Groups
from utils.path import create


def remove_repated(groups):
    ans = [None]
    for group in sorted(groups, key=lambda g: g.act):
        if not group.is_same(ans[-1], 0.7):
            ans.append(group)
    return ans[1:]


def print_statistics(data_dir = definitions.OUT_DIR):
    apps = [d for d in os.scandir(data_dir) if d.is_dir()]
    group_nums = []
    unique_nums = []
    no_groups = 0
    for app in apps:
        groups = Groups.from_folder(app.path, app.name)
        # if len(groups) > 0:
        #     print(groups[0].complexity())
        #     exit()
        if len(groups) == 0:
            no_groups += 1
            continue
        group_nums.append(len(groups))
        groups = [g for g in remove_repated(groups) if g.enough_nodes(5)]
        # unique_nums.append(len(groups))
        unique_nums.append(min(40, len(groups)))

        if len(groups) > 100:
            print(f"{app} has {len(groups)} groups")
            # print(min([g for g in groups], key=minfunc))
    print(f"total pairs: {sum(group_nums)}")
    print(f"unique pairs: {sum(unique_nums)}")

    with open(definitions.FAIL_LOG_PATH) as f:
        lines = f.readlines()
        print(f"total number of apps: {len(lines) + len(apps)}")
        print(f"number of succeed apps: {len(apps)}")
        print(f"apps has no pairs: {no_groups}")
        print(f"failed apps: {len(lines)}")
    plot(unique_nums)


def plot(nums):
    print(nums)
    import seaborn as sns
    # plot = sns.lineplot(x=range(0, len(unique_nums)), y=unique_nums)
    sns.histplot(nums, binwidth=1)
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
    groups = Groups.from_folder(os.scandir(os.path.join(definitions.DATA_DIR, "com.twitter.android")))
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
        gs = filter(lambda g: g.is_legit(), Groups.from_folder(path, entry.name))
        gs = sorted(gs, key=lambda g:g.complexity())
        gs = list({g.act: g for g in gs}.values())[:40]
        for g in gs:
            out = definitions._create(os.path.join(definitions.DATA_DIR, "unique", entry.name))
            # print(out)
            g.copy_to(out)


def move_to_unique2():
    gs = filter(lambda g: g.is_legit(), Groups.from_out_dir())
    gs = sorted(gs, key=lambda g: (g.act, g.id))
    prev = None
    out = lambda pkg: definitions._create(os.path.join(definitions.DATA_DIR, "unique2", pkg))
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
        return min(d[0],d[1]), c
    out = os.path.join(definitions.DATA_DIR, "unique")
    gs = sorted((g for g in Groups.from_out_dir(out) if g.is_legit()), key=total_div, reverse=True)
    i = 0
    for g in gs:
        out = create(os.path.join(definitions.DATA_DIR, "example", g.pkg))
        print(g)
        i += 1
        if i == 100:
            exit()
        g.copy_to(out)
        # g.draw(out, "leaf")


if __name__ == "__main__":
    # TODO xml into 5 components
        # know classes
        # how to map?
    # TODO xml complexity by class type
    # test_diversity()
    print_statistics()
    # print_statistics(definitions.DATA_DIR+"/unique")
    # remove()
    # move_to_unique()


