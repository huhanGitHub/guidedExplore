import os
import re
import definitions
from itertools import groupby, chain, pairwise
from utils.xml_helpers import *
from xml.etree import ElementTree
from utils.path import name_to_map
from pathlib import Path

def act_name(f):
    if type(f) is os.DirEntry:
        f = f.name
    return f.split('_')[2]

# rate: 0.3714
# rate: 0.0357

def check_repeated(path, remove=False):
    fs = os.scandir(path)
    fs = [f for f in fs if 'phone' in f.name and f.name.endswith(".xml")]
    fs = sorted(fs, key=act_name)
    c = 0
    cpx = 0
    for i in range(0, len(fs)-1):
        f1 = fs[i]
        f2 = fs[i-1]
    # for (f1, f2) in pairwise(fs):
        s1 = Path(f1).read_text()
        s2 = Path(f2).read_text()
        if xml_complexity(f1) < 10:
            cpx += 1
            c += 1
            continue
        if is_same_activity(s1, s2, 0.8):
            c +=1
    print(f"""total: {len(fs)}
            too simple: {cpx}
            simple or repated: {c}, rate: {c / len(fs)},
            usable: {len(fs) - c}
            """
    )

def group_id(f):
    if type(f) is os.DirEntry:
        f = f.name
    return f.split('_')[0]

def complexity(lst):
    xs = {i[0]: i for i in lst}.keys()
    ys = {i[1]: i for i in lst}.keys()
    print(xs)
    print(ys)
    return (len(xs), len(ys))

def bounds2p(b):
    (x1, y1, x2, y2) = bounds2int(b)
    return x1, y1
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    return x, y


p = os.path.join(definitions.DATA_DIR, "test_complexity")
groups = groupby(sorted(os.scandir(p), key=group_id), group_id)

for group in groups:
    print(group[0])
    files = [f for f in group[1] if f.name.endswith('.xml')]
    for f in files:
        print(f)
        tree = ElementTree.fromstring(Path(f).read_text())
        tree = remove_sysui(tree)
        nodes = [n for n in tree.iter('*') if len(n) == 0]
        # nodes = tree_to_list(tree)
        bounds = [n.attrib.get('bounds') for n in nodes]
        # bounds = re.findall(r'\[.*\]', Path(f).read_text())
        bounds = [bounds2p(b)for b in bounds]
        a = complexity(bounds)
        print(a,end='\n\n')


# p = os.path.join(definitions.DATA_DIR, 'com.twitter.android_clickables')
# check_repeated(p)
# p = os.path.join(definitions.DATA_DIR, 'com.twitter.android')
# check_repeated(p)
# fs = [f for f in os.scandir(os.path.join(definitions.DATA_DIR, 'com.twitter.android_clickables'))]
# print(len(fs))

# d = Device(definitions.TABLET_ID)
# print(d.info)
# d = Device(definitions.VM_ID)
# print(d.info)

