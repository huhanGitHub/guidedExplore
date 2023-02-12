# guidedExplore
Step 1: install required packages in the requirement.txt
`pip install -r requirement.txt`

Step 2:
set the following configuration of this test in the dynamic_testing/dynamic_GUI_testing.py：

```python
deviceId = '192.168.57.105'
apk_path = r'../data/repackaged_apks/youtube.apk'
atg_json = r'../data/activity_atg/youtube.json'
deeplinks_json = r'../data/deeplinks/youtube.json'
log = r'../data/visited_rate/youtube.txt'
```
    
 Then, run this script to explore apps.
 
 We provide two pre-injected example apps: youtube and EZ explorer in the data/repackaged_apks.
 Note that the apks are all pre-injected into deeplinks and extracted intent parameters and atg in the deeplinks_json and atg_json.
 There may be unpredictable issues, so pls run each app multiple times.
 Pre-login and granting permission in advance will improve the effectiveness of app exploration.
 The code here is not the latest version, but it can still achieve state-of-the-art.
 
 #### Command Line Interface
 `python main.py`
 
#### NOTE
- resolution and orientation
    - if device x-axis is at longer side (i.e Device().infoand some at shorter side
2. larger numer of apks


## About Our dataset
Please cite our paper if you use the dataset:
....

The dataset includes UI object type labels (e.g., BUTTON, IMAGE, CHECKBOX) that describe a UI object's semantic type on Android app screenshots. It is used to ...

Each screenshot has four files (png and XML for both phone and tablet), which are located at `data/<app_id>/` with file name pattern `<pair_id>_<device_type>_<activiey_name>.<file_type>`.

XML files contain the entire UI object captured by `uiautomator2` at runtime. Each node in the object contained necessary attributes such as `class` and `bounds`. PNG files are also provided for visual comparison and debugging purposes.

The entire data collection pipeline is the following:
1. Using `scraper.js` to scrap apps from the google app store and save it to file `apps.json` (mainly to get'add_id` for downloading).
2. Use `download_apks.py` to download. Note [apkeep](https://github.com/EFForg/apkeep) is required.
3. Update necessary variables inside `definitions.py`.
4. Run `main.py` to collect the data.
