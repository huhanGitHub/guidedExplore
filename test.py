from PIL import Image, ImageDraw, ImageFont
import definitions
from definitions import DATA_DIR
from os.path import join
from utils.xml_helpers import bounds2int, clickable_bounds, tree_to_list
from pathlib import Path
from xml.etree import ElementTree
from math import sin, cos
import colorsys


def rgb(phi):
    u = 255 / 4 * cos(phi)
    v = 255 / 4 * sin(phi)
    y = 255 / 2
    r = int(y + v / 0.88)
    g = int(y - 0.38 * u - 0.58 * v)
    b = int(y + u / 0.49)
    return (r, g, b)


def even_colors(n):
    return ["blue", "red", "yellow", "orange", "purple"]
    # return [rgb(n) for n in range(0, 360, 360//n)]


def HSVToRGB(h, s, v):
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    return (int(255 * r), int(255 * g), int(255 * b))


def getDistinctColors(n):
    huePartition = 1.0 / (n + 1)
    return (HSVToRGB(huePartition * value, 1.0, 1.0) for value in range(0, n))


def draw_bounds(
    image_path=join(
        DATA_DIR, "test", "AboutActivity_1657966977_tablet_AboutActivity_a_a.png"
    ),
    xml_path=join(
        DATA_DIR, "test", "AboutActivity_1657966977_tablet_AboutActivity_a_a.xml"
    ),
):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    s = Path(xml_path).read_text()
    t = ElementTree.fromstring(s)
    es = tree_to_list(t)
    classes = set([e.attrib["class"] for e in es])
    colors = even_colors(len(classes))
    color_map = {c: color for (c, color) in zip(classes, colors)}
    print(color_map)
    # font = ImageFont.truetype("arial.ttf", 15)
    font = ImageFont.truetype("SpaceMono-Regular.ttf", 24)

    for element in tree_to_list(t):
        bounds = bounds2int(element.attrib["bounds"])
        cls = element.attrib["class"]
        color = color_map[cls]

        draw.rectangle(bounds, outline=color, width=3)
        draw.text((bounds[0], bounds[1]), cls, font=font, fill=color)

    image.save(join(DATA_DIR, "test.png"))


COLOR_MAP = {
    "android.view.MenuItem": (255, 0, 0),
    "android.view.View": (255, 30, 0),
    "android.widget.TextView": (255, 60, 0),
    "android.widget.FrameLayout": (255, 89, 0),
    "android.widget.LinearLayout": (255, 120, 0),
    "android.widget.Button": (255, 150, 0),
    "android.widget.ImageView": (255, 179, 0),
    "android.widget.ImageButton": (255, 210, 0),
    "android.view.ViewGroup": (255, 240, 0),
    "android.widget.ScrollView": (240, 255, 0),
    "android.widget.RelativeLayout": (210, 255, 0),
    "android.widget.EditText": (179, 255, 0),
    "androidx.recyclerview.widget.RecyclerView": (150, 255, 0),
    "android.widget.ListView": (120, 255, 0),
    "android.webkit.WebView": (89, 255, 0),
    "android.widget.RadioButton": (60, 255, 0),
    "android.widget.CheckBox": (30, 255, 0),
    "android.widget.Image": (0, 255, 0),
    "android.widget.Switch": (0, 255, 29),
    "android.widget.ProgressBar": (0, 255, 60),
    "android.widget.Spinner": (0, 255, 90),
    "androidx.viewpager.widget.ViewPager": (0, 255, 120),
    "android.widget.ToggleButton": (0, 255, 150),
    "android.widget.HorizontalScrollView": (0, 255, 180),
    "androidx.drawerlayout.widget.DrawerLayout": (0, 255, 209),
    "android.widget.CheckedTextView": (0, 255, 239),
    "androidx.appcompat.app.ActionBar$b": (0, 240, 255),
    "androidx.appcompat.widget.LinearLayoutCompat": (0, 209, 255),
    "androidx.appcompat.app.ActionBar$Tab": (0, 179, 255),
    "androidx.cardview.widget.CardView": (0, 150, 255),
    "android.widget.SeekBar": (0, 120, 255),
    "s1.a": (0, 90, 255),
    "android.widget.GridView": (0, 60, 255),
    "msa.apps.podcastplayer.widget.slidingpanelayout.SlidingPaneLayout": (0, 29, 255),
    "android.support.v7.widget.RecyclerView": (0, 0, 255),
    "android.widget.TwoLineListItem": (29, 0, 255),
    "android.widget.RatingBar": (59, 0, 255),
    "android.app.ActionBar$Tab": (89, 0, 255),
    "android.widget.CompoundButton": (120, 0, 255),
    "android.widget.VideoView": (149, 0, 255),
    "android.widget.SearchView": (180, 0, 255),
    "android.widget.TabWidget": (210, 0, 255),
    "android.widget.NumberPicker": (240, 0, 255),
    "androidx.appcompat.app.a$c": (255, 0, 240),
    "android.widget.DatePicker": (255, 0, 209),
    "com.real.IMP.ui.view.TableView": (255, 0, 180),
    "android.appwidget.AppWidgetHostView": (255, 0, 149),
    "android.app.Dialog": (255, 0, 120),
    "android.widget.TabHost": (255, 0, 90),
    "com.android.internal.widget.ViewPager": (255, 0, 60),
}


def color_mapper(m=COLOR_MAP):
    colors = getDistinctColors(len(m))
    print({k: v for (k, v) in zip(m.keys(), colors)})



if __name__ == "__main__":
    # color_mapper()
    import random
    ks = list(COLOR_MAP)
    random.shuffle(ks)
    cls = list(ks)[:10]
    print(" || ".join(cls))

