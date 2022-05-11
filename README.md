# guidedExplore
Step 1: install required packages in the requirement.txt

Step 2:
Set the following configuration of this test in the dynamic_testing/dynamic_GUI_testing.py：

    deviceId = '192.168.57.105'
    # deviceId = 'cb8c90f4'
    # deviceId = 'VEG0220B17010232'
    apk_path = r'../data/repackaged_apks/youtube.apk'
    atg_json = r'../data/activity_atg/youtube.json'
    deeplinks_json = r'../data/deeplinks_params.json'
    log = r'../data/visited_rate/youtube.txt'
    
 Then, run this script to explore apps.
 
 Note that the apks are all pre-injected into deeplinks and extracted intent parameters and atg in the atg_json and deeplinks_json.
 We provide two example apps: youtube and EZ explorer.
 There may be unpredictable issues, so pls run each app multiple times.
 Lgging in and granting permission in advance will help a lot.
 The code here is not the latest version, but it can still achieve state-of-the-art.
 
