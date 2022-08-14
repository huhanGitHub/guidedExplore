import os
import shutil
from itertools import groupby
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import definitions

from utils.path import basename_no_ext
from utils.xml_helpers import *
from color_map import COLOR_MAP
 

def bounds2xy(bounds):
    xs = {i[0]: i for i in bounds}.keys()
    ys = {i[1]: i for i in bounds}.keys()
    return xs, ys


def group_id(f):
    if type(f) is os.DirEntry:
        f = f.name
    return f.split("_")[0]


def get_act(f):
    if type(f) is os.DirEntry:
        f = basename_no_ext(f.name)
    return f.split("_")[2]


class Groups:
    def from_folder(f, pkg=None):
        files = os.scandir(f)
        if pkg is None:
            pkg = os.path.basename(f)
        groups = groupby(sorted(files, key=group_id), group_id)
        groups = [Group(g, pkg) for g in groups]
        return groups

    def from_out_dir(out_dir=definitions.OUT_DIR):
        return [
            g
            for app in os.scandir(out_dir)
            for g in Groups.from_folder(app.path, app.name)
        ]


class Group:
    def __init__(self, group, pkg):
        self.id = group[0]
        self.pkg = pkg
        self.files = list(group[1])
        self.act = get_act(self.files[0])
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

    def __repr__(self):
        return self.id + self.act

    def is_same(self, other):
        if other is None:
            return False
        if self.act != other.act:
            return False

        def content(entry):
            return Path(entry.path).read_text()

        return is_same_activity(
            content(self.txml), content(other.txml), 0.9
        ) and is_same_activity(content(self.pxml), content(other.pxml), 0.9)

    def copy_to(self, dest):
        for f in self.files:
            # dest = os.path.join(dest, f.name)
            shutil.copy(f.path, dest)

    def ptree(self):
        try:
            return self._ptree
        except AttributeError:
            self._ptree = path2tree(self.pxml)
            return self._ptree

    def ttree(self):
        try:
            return self._ttree
        except AttributeError:
            self._ttree = path2tree(self.txml)
            return self._ttree

    def node_num(self):
        try:
            return self._pn, self._tn
        except AttributeError:
            self._pn = len(self.ptree().findall(f".//node[@package='{self.pkg}']"))
            self._tn = len(self.ttree().findall(f".//node[@package='{self.pkg}']"))
            return self._pn, self._tn

    def enough_nodes(self, target=5):
        pn, tn = self.node_num()
        return pn >= target and tn >= target

    def xy_complexity(self):
        (px, py) = bounds2xy(xml_to_bounds(self.pxml.path))
        (tx, ty) = bounds2xy(xml_to_bounds(self.txml.path))
        return list(map(len, (px, py, tx, ty)))

    def xy_complex_enough(self, target=5):
        for b in self.xy_complexity():
            if b < target:
                return False
        return True

    def classes(self):
        p = classes(self.ptree(), self.pkg)
        t = classes(self.ttree(), self.pkg)
        return (p, t)

    def diversity(self):
        c = self.classes()
        return len(c[0]), len(c[1])

    def diverse_enough(self, target=3):
        d = self.diversity()
        return d[0] >= target and d[1] >= target

    def complexity(self):
        d = self.diversity()
        c = sum(self.xy_complexity())
        return min(d[0],d[1]), c

    def is_legit(self):

        return (len(self.files) == 4
                and self.is_paired() and self.complex_enough() and self.diverse_enough())

    def is_paired(self):
        # NOTE: naive
        return get_act(self.pxml) == get_act(self.txml)

    def complex_enough(self):
        return self.enough_nodes(10)

    def draw(self, out, elements="all"):
        assert os.path.isdir(out)
        for png, tree in [(self.ppng, self.ptree()), (self.tpng, self.ttree())]:
            drawed = set()
            image = Image.open(png.path)
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("SpaceMono-Regular.ttf", 20)

            if elements == "all":
                es = (e for e in tree.findall(f".//node[@package='{self.pkg}']"))
            elif elements == "leaf":
                es = (e for e in tree.findall(f".//node[@package='{self.pkg}']") if len(e) == 0)
            elif elements == "nonleaf":
                es = (e for e in tree.findall(f".//node[@package='{self.pkg}']") if len(e) != 0)
            else:
                es = elements.pop(0)

            for element in es:
                bounds = bounds2int(element.attrib["bounds"])
                cls = element.attrib["class"]
                color = COLOR_MAP[cls]
                draw.rectangle(bounds, outline=color, width=3)
                # if cls not in drawed:
                draw.text((bounds[0], bounds[1]), cls, font=font, fill=color)
                drawed.add(cls)
            # TODO
            out_png = os.path.join(out, png.name)
            image.save(out_png)

    def group_element(self):
        pass


if __name__ == "__main__":
    gs = Groups.from_folder(os.path.join(definitions.DATA_DIR, "test"))
    for g in gs:
        if g.id == "1658834980":
            g.pkg = "com.android.vending"
            print(g.diversity() > (10, 10))
    # gs = list(g.diversity() for g in gs if g.id == "1658834980")
    # print(gs)
