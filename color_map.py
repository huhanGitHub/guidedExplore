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


CLASS_MAP = {
    "tab": "tab",
    "android.app.ActionBar$Tab": "tab",
    "androidx.appcompat.app.ActionBar$Tab": "tab",
    "androidx.appcompat.app.ActionBar$b": "tab",
    "androidx.appcompat.app.a$c": "tab",
    "android.widget.TabHost": "tab",
    "android.widget.TabWidget": "tab",
    "android.widget.HorizontalScrollView": "tab",
    "text": "text",
    "android.widget.EditText": "text",
    "android.widget.MultiAutoCompleteTextView": "text",
    "android.widget.TextView": "text",
    "android.app.Dialog": "text",
    "control": "control",
    "android.widget.Button": "control",
    "android.widget.ImageButton": "control",
    "android.widget.ToggleButton": "control",
    "android.widget.CheckBox": "control",
    "android.widget.CheckedTextView": "control",
    "android.widget.CompoundButton": "control",
    "android.widget.DatePicker": "control",
    "android.widget.NumberPicker": "control",
    "android.widget.ProgressBar": "control",
    "android.widget.RadialTimePickerView$RadialPickerTouchHelper": "control",
    "android.widget.RadioButton": "control",
    "android.widget.RadioGroup": "control",
    "android.widget.RatingBar": "control",
    "android.widget.SeekBar": "control",
    "android.widget.Switch": "control",
    "android.widget.Spinner": "control",
    "image": "image",
    "android.widget.Image": "image",
    "android.widget.ImageView": "image",
    "android.widget.VideoView": "image",
    "android.webkit.WebView": None,
    "listview": "listview",
    "android.support.v7.widget.RecyclerView": None,
    "androidx.recyclerview.widget.RecyclerView": None,
    "android.widget.ListView": None,
    None: None,
    "android.widget.FrameLayout": None,
    "android.appwidget.AppWidgetHostView": None,
    "android.support.v4.widget.DrawerLayout": None,
    "android.view.MenuItem": None,
    "android.view.View": None,
    "android.view.ViewGroup": None,
    "android.widget.AdapterView": None,
    "android.widget.Gallery": None,
    "android.widget.GridView": None,
    "android.widget.LinearLayout": None,
    "android.widget.RelativeLayout": None,
    "android.widget.ScrollView": None,
    "android.widget.SearchView": None,
    "android.widget.TwoLineListItem": None,
    "androidx.appcompat.widget.LinearLayoutCompat": None,
    "androidx.cardview.widget.CardView": None,
    "androidx.drawerlayout.widget.DrawerLayout": None,
    "androidx.viewpager.widget.ViewPager": None,
    "c.s.a.b": None,
    "com.android.internal.widget.ViewPager": None,
    "com.real.IMP.ui.view.TableView": None,
    "msa.apps.podcastplayer.widget.slidingpanelayout.SlidingPaneLayout": None,
    "my.group": None,
    "s1.a": None,
    "ট": None,
    "com.google.android.material.chip.Chip": None,
}


# leaf mode color
COLOR_MAP = {
    "topbar": "cyan",
    "tab": "cyan",
    "android.app.ActionBar$Tab": "cyan",
    "androidx.appcompat.app.ActionBar$Tab": "cyan",
    "androidx.appcompat.app.ActionBar$b": "cyan",
    "androidx.appcompat.app.a$c": "cyan",
    "android.widget.TabHost": "cyan",
    "android.widget.TabWidget": "cyan",
    "android.widget.HorizontalScrollView": "cyan",
    "text": "green",
    "android.widget.EditText": "green",
    "android.widget.MultiAutoCompleteTextView": "green",
    "android.widget.TextView": "green",
    "android.app.Dialog": "green",
    "control": "olive",
    "android.widget.Button": "olive",
    "android.widget.ImageButton": "olive",
    "android.widget.ToggleButton": "olive",
    "android.widget.CheckBox": "olive",
    "android.widget.CheckedTextView": "olive",
    "android.widget.CompoundButton": "olive",
    "android.widget.DatePicker": "olive",
    "android.widget.FrameLayout": "olive",
    "android.widget.NumberPicker": "olive",
    "android.widget.ProgressBar": "olive",
    "android.widget.RadialTimePickerView$RadialPickerTouchHelper": "olive",
    "android.widget.RadioButton": "olive",
    "android.widget.RadioGroup": "olive",
    "android.widget.RatingBar": "olive",
    "android.widget.SeekBar": "olive",
    "android.widget.Spinner": "olive",
    "android.widget.Switch": "olive",
    "image": "purple",
    "android.widget.Image": "purple",
    "android.widget.ImageView": "purple",
    "android.widget.VideoView": "purple",
    "listview": "black",
    "android.support.v7.widget.RecyclerView": "black",
    "androidx.recyclerview.widget.RecyclerView": "black",
    "android.widget.ListView": "black",
    "android.webkit.WebView": "red",
    "": "red",
    "android.appwidget.AppWidgetHostView": "red",
    "android.support.v4.widget.DrawerLayout": "red",
    "android.view.MenuItem": "red",
    "android.view.View": "red",
    "android.view.ViewGroup": "red",
    "android.widget.AdapterView": "red",
    "android.widget.Gallery": "red",
    "android.widget.GridView": "red",
    "android.widget.LinearLayout": "red",
    "android.widget.RelativeLayout": "red",
    "android.widget.ScrollView": "red",
    "android.widget.SearchView": "red",
    "android.widget.TwoLineListItem": "red",
    "androidx.appcompat.widget.LinearLayoutCompat": "red",
    "androidx.cardview.widget.CardView": "red",
    "androidx.drawerlayout.widget.DrawerLayout": "red",
    "androidx.viewpager.widget.ViewPager": "red",
    "c.s.a.b": "red",
    "com.android.internal.widget.ViewPager": "red",
    "com.real.IMP.ui.view.TableView": "red",
    "msa.apps.podcastplayer.widget.slidingpanelayout.SlidingPaneLayout": "red",
    "my.group": "red",
    "s1.a": "red",
    "ট": "red",
    "com.google.android.material.chip.Chip": "red",
}


def return_v(i):
    return i[1]


def color_mapper(m=COLOR_MAP):
    colors = getDistinctColors(len(m))
    print({k: v for (k, v) in zip(m.keys(), colors)})
