# News
We are pleased to note that our tool, along with its variants, have been utilized and contributed to the following works:

[Papt dataset](https://github.com/huhanGitHub/papt) (accepted by NeurIPS 2023). [Paper](https://arxiv.org/abs/2310.04755)

[Voicify](https://github.com/vuminhduc796/Voicify) (accepted by Ubicomp 2023). [Paper](https://arxiv.org/pdf/2305.05198.pdf)



# guidedExplore
Step 1: install required packages in the requirement.txt

Step 2:
set your configuration of this test in the dynamic_testing/dynamic_GUI_testing.py.
The default settings of ATG (atg_json) and deep links (deeplinks_json) can be used for provided demo APKs.

    deviceId = '192.168.57.105'
    # deviceId = 'cb8c90f4'
    apk_path = r'../data/repackaged_apks/youtube.apk'
    atg_json = r'../data/activity_atg/youtube.json'
    deeplinks_json = r'../data/deeplinks_params.json'
    log = r'../data/visited_rate/youtube.txt'
    
 Then, run this script to explore apps. We embded simple Monkey test in our script.
 
 We provide two pre-injected example apps: youtube and EZ explorer in the data/repackaged_apks.
 Note that the apks are all pre-injected into deeplinks and extracted intent parameters and atg in the deeplinks_json and atg_json.
 There may be unpredictable issues, so pls run each app multiple times.
 Pre-login and granting permission in advance will improve the effectiveness of app exploration.
 
 The code here is not the latest version, but it can still achieve state-of-the-art.
 
