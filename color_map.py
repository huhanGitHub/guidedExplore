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


COLOR_MAP = {
    "android.app.Dialog": (255, 0, 0),
    "androidx.viewpager.widget.ViewPager": (255, 26, 0),
    "android.view.ViewGroup": (255, 52, 0),
    "androidx.recyclerview.widget.RecyclerView": (255, 79, 0),
    "android.widget.Gallery": (255, 105, 0),
    "android.view.MenuItem": (255, 131, 0),
    "android.widget.VideoView": (255, 158, 0),
    "android.widget.Button": (255, 184, 0),
    "android.widget.NumberPicker": (255, 211, 0),
    "android.widget.RadioButton": (255, 237, 0),
    "msa.apps.podcastplayer.widget.slidingpanelayout.SlidingPaneLayout": (246, 255, 0),
    "android.widget.MultiAutoCompleteTextView": (219, 255, 0),
    "android.widget.HorizontalScrollView": (193, 255, 0),
    "androidx.drawerlayout.widget.DrawerLayout": (167, 255, 0),
    "android.support.v4.widget.DrawerLayout": (167, 255, 0),
    "android.widget.LinearLayout": (140, 255, 0),
    "android.app.ActionBar$Tab": (114, 255, 0),
    "android.widget.ToggleButton": (87, 255, 0),
    "android.widget.FrameLayout": (61, 255, 0),
    "android.widget.ProgressBar": (35, 255, 0),
    "android.widget.CheckedTextView": (8, 255, 0),
    "android.widget.RelativeLayout": (0, 255, 17),
    "android.widget.ImageView": (0, 255, 43),
    'com.google.android.material.chip.Chip':  (0, 255, 43),
    "com.android.internal.widget.ViewPager": (0, 255, 70),
    "android.widget.EditText": (0, 255, 96),
    "s1.a": (0, 255, 123),
    "android.widget.CompoundButton": (0, 255, 149),
    "androidx.appcompat.app.ActionBar$b": (0, 255, 175),
    "android.widget.RadioGroup": (0, 255, 202),
    "android.view.View": (0, 255, 228),
    "android.widget.TabHost": (0, 255, 255),
    "android.widget.Switch": (0, 228, 255),
    "android.widget.DatePicker": (0, 202, 255),
    "android.widget.SeekBar": (0, 175, 255),
    "androidx.appcompat.app.a$c": (0, 149, 255),
    "android.widget.TabWidget": (0, 123, 255),
    "android.widget.ListView": (0, 96, 255),
    "android.widget.SearchView": (0, 70, 255),
    "android.widget.AdapterView": (0, 43, 255),
    "android.support.v7.widget.RecyclerView": (0, 17, 255),
    "android.widget.TextView": (8, 0, 255),
    "android.widget.CheckBox": (35, 0, 255),
    "android.widget.GridView": (61, 0, 255),
    "android.widget.Image": (87, 0, 255),
    "androidx.appcompat.widget.LinearLayoutCompat": (114, 0, 255),
    "android.widget.Spinner": (140, 0, 255),
    "android.widget.ScrollView": (167, 0, 255),
    "android.appwidget.AppWidgetHostView": (193, 0, 255),
    "androidx.appcompat.app.ActionBar$Tab": (219, 0, 255),
    "c.s.a.b": (246, 0, 255),
    "android.widget.RatingBar": (255, 0, 237),
    "com.real.IMP.ui.view.TableView": (255, 0, 211),
    "android.widget.ImageButton": (255, 0, 184),
    "androidx.cardview.widget.CardView": (255, 0, 158),
    "ট": (255, 0, 131),
    "android.widget.RadialTimePickerView$RadialPickerTouchHelper": (255, 0, 105),
    "android.webkit.WebView": (255, 0, 79),
    "android.widget.TwoLineListItem": (255, 0, 52),
    "my.group": (255, 0, 52),
}




def color_mapper(m=COLOR_MAP):
    colors = getDistinctColors(len(m))
    print({k: v for (k, v) in zip(m.keys(), colors)})
