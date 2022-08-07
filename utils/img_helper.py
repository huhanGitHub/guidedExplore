from math import cos, sin
from os.path import join
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, ImageDraw, ImageFont

from definitions import DATA_DIR
from utils.xml_helpers import bounds2int, tree_to_list


def rgb(phi):
    u = 255 / 4 * cos(phi)
    v = 255 / 4 * sin(phi)
    y = 255 / 2
    r = int(y + v / 0.88)
    g = int(y - 0.38 * u - 0.58 * v)
    b = int(y + u / 0.49)
    return (r, g, b)


def even_colors(n):
    # return ["blue", "red", "yellow", "orange", "purple"]
    return [rgb(n) for n in range(0, 360, 360 // n)]


def color_mapper():
    {
        "android.view.View": 27660,
        "android.widget.TextView": 27600,
        "android.widget.FrameLayout": 8777,
        "android.widget.LinearLayout": 5797,
        "android.widget.Button": 3128,
        "android.widget.ImageView": 3115,
        "android.widget.ImageButton": 2840,
        "android.view.ViewGroup": 2740,
        "android.widget.ScrollView": 1871,
        "android.widget.RelativeLayout": 1855,
        "android.widget.EditText": 1489,
        "androidx.recyclerview.widget.RecyclerView": 1325,
        "android.widget.ListView": 993,
        "android.webkit.WebView": 737,
        "android.widget.RadioButton": 670,
        "android.widget.CheckBox": 633,
        "android.widget.Image": 483,
        "android.widget.Switch": 409,
        "android.widget.ProgressBar": 385,
        "android.widget.Spinner": 359,
        "androidx.viewpager.widget.ViewPager": 292,
        "android.widget.ToggleButton": 286,
        "android.widget.HorizontalScrollView": 257,
        "androidx.drawerlayout.widget.DrawerLayout": 186,
        "android.widget.CheckedTextView": 163,
        "androidx.appcompat.app.ActionBar$b": 147,
        "androidx.appcompat.widget.LinearLayoutCompat": 145,
        "androidx.appcompat.app.ActionBar$Tab": 98,
        "androidx.cardview.widget.CardView": 79,
        "android.widget.SeekBar": 71,
        "s1.a": 47,
        "android.widget.GridView": 29,
        "msa.apps.podcastplayer.widget.slidingpanelayout.SlidingPaneLayout": 27,
        "android.support.v7.widget.RecyclerView": 26,
        "android.widget.TwoLineListItem": 17,
        "android.widget.RatingBar": 12,
        "android.app.ActionBar$Tab": 10,
        "android.widget.CompoundButton": 10,
        "android.widget.VideoView": 9,
        "android.widget.SearchView": 9,
        "android.widget.TabWidget": 8,
        "android.widget.NumberPicker": 6,
        "androidx.appcompat.app.a$c": 2,
        "android.widget.DatePicker": 2,
        "com.real.IMP.ui.view.TableView": 2,
        "android.appwidget.AppWidgetHostView": 2,
        "android.app.Dialog": 2,
        "android.widget.TabHost": 2,
        "com.android.internal.widget.ViewPager": 1,
    }


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
