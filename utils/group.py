import os
import csv
import shutil
from itertools import groupby,tee
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


def group_id(f_name):
    if type(f_name) is os.DirEntry:
        f_name = f_name.name
    return f_name.split("_")[0]


def get_act(f_name):
    if type(f_name) is os.DirEntry:
        f_name = basename_no_ext(f_name.name)
    return f_name.split("_")[2]


class Groups:
    def from_folder(f, pkg):
        files = os.scandir(f)

        def from_groupby(g):
            id = g[0]
            entries, c = tee(g[1], 2)
            act = get_act(next(c))
            return Group(id, pkg, act, list(entries))
        groups = groupby(sorted(files, key=group_id), group_id)
        groups = [from_groupby(g) for g in groups]
        return groups

    def from_out_dir(out_dir=definitions.OUT_DIR):
        """folder of folders"""
        return [
            g
            for app in os.scandir(out_dir)
            for g in Groups.from_folder(app.path, app.name)
        ]

    def from_scv(csv_path):
        with open(csv_path) as f:
            reader = csv.reader(f)
            next(reader)
            lines = list(reader)
            base = os.path.dirname(csv_path)
            files = lambda p : os.scandir(os.path.join(base, p))
            return [Group(l[3], l[0], l[1], files(l[3])) for l in lines]


class Group:
    def __init__(self, id, pkg, act, files):
        self.pkg = pkg
        self.act = act
        self.id = id
        # entries
        self.files = files
        for f in files:
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
    # def __init__(self, group, pkg=None):
    #     self.id = group[0]
    #     self.pkg = pkg
    #     self.files = list(group[1])
    #     self.act = get_act(self.files[0])
    #     for f in self.files:
    #         if f.name.endswith(".xml"):
    #             if "phone" in f.name:
    #                 self.pxml = f
    #             else:
    #                 self.txml = f
    #         else:
    #             if "phone" in f.name:
    #                 self.ppng = f
    #             else:
    #                 self.tpng = f

    def __repr__(self):
        return f"{self.id} {self.act} {self.pkg}"

    def is_same(self, other, rate=0.9):
        if other is None:
            return False
        if self.act != other.act:
            return False

        def content(entry):
            return Path(entry.path).read_text()

        return is_same_activity(
            content(self.txml), content(other.txml), rate
        ) and is_same_activity(content(self.pxml), content(other.pxml), rate)

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

    def has_keyboard(self):
        return exits_keyboard(self.ttree()) or exits_keyboard(self.ptree())

    def is_legit(self):
        return (len(self.files) == 4
                and self.is_paired()
                and self.complex_enough()
                and self.diverse_enough()
                and not self.has_keyboard())

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

    def wireframe(self, elements, ret):
        def draw_wireframe(image, tree, xbase, color_map=COLOR_MAP):
            draw = ImageDraw.Draw(image)
            if elements == "all":
                es = (e for e in tree.findall(f".//node[@package='{self.pkg}']"))
            elif elements == "leaf":
                es = (e for e in tree.findall(f".//node[@package='{self.pkg}']") if len(e) == 0)
            elif elements == "nonleaf":
                es = (e for e in tree.findall(f".//node[@package='{self.pkg}']") if len(e) != 0)
            else:
                es = elements

            for element in es:
                bounds = bounds2int(element.attrib["bounds"])
                bounds[0] += xbase
                bounds[2] += xbase
                cls = element.attrib["class"]
                color = color_map[cls]
                draw.rectangle(bounds, outline=color, width=3)

        pimage = Image.open(self.ppng.path)
        timage = Image.open(self.tpng.path)
        # tsize = timage.size
        size = timage.size
        if ret == "join":
            new_image = Image.new('RGB',(2*size[0], size[1]), (255,255,255))
            draw_wireframe(new_image, self.ttree(), size[0])
            # phone
            pimage = Image.new('RGB', pimage.size, (255,255,255))
            draw_wireframe(pimage, self.ptree(), 0)
            pimage.thumbnail(size, Image.ANTIALIAS)
            # pimage.resize(size)
            new_image.paste(pimage, (0, 0))
            # screen bounds
            draw = ImageDraw.Draw(new_image)
            x, y = pimage.size
            draw.line((x, 0, x, y), fill=(0,0,0), width=2)
            x, y = timage.size
            draw.line((x, 0, x, y), fill=(0,0,0), width=2)
            return new_image
        elif ret == "split":
            pimage = Image.new('RGB', pimage.size, (250,250,250))
            draw_wireframe(pimage, self.ptree(), 0)
            timage = Image.new('RGB',timage.size, (250,250,250))
            draw_wireframe(timage, self.ttree(), 0)
            return pimage, timage
        else:
            raise RuntimeError("unknown ret argument")

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
