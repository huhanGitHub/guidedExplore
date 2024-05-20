# News
We are pleased to note that our tool, along with its variants, have been utilized and contributed to the following works:

[Papt dataset](https://github.com/huhanGitHub/papt) (accepted by NeurIPS 2023). [Paper](https://arxiv.org/abs/2310.04755)

[Voicify](https://github.com/vuminhduc796/Voicify) (accepted by Ubicomp 2023). [Paper](https://arxiv.org/pdf/2305.05198.pdf)


# Delm (Enhancing GUI Exploration Coverage of Android Apps with Deep Link-Integrated Monkey, TOSEM 2024)
The paper of the tool Delm has experienced many resubmissions and revisions. Initially, this project was launched at the start of my PhD and formed the basis for all my subsequent PhD projects. Interestingly, it was the last piece to be accepted by a top-tier venue during my PhD. There were times we even considered abandoning the paper, leading to adjustments in the tool's features to better serve my other my PhD works.

The current version of the code primarily differs from the one discussed in the paper in two key aspects:

(1) To maximize the exploration of GUI pages across various Android activities, we have relaxed the requirements for activity context accuracy. We now manually simulate activity contexts with the required types and numbers to launch more activities and thus collect more GUI pages.

(2) We have disabled the dynamic guided exploration component because it was too time-consuming. Currently, we use the ATG to sequentially launch activities.


Delm is now primarily used as a GUI collection tool in my later works, not as a testing tool. We have modified the configuration to enable the exploration of as many GUI pages as possible. If you intend to use it for GUI page collection, this version of the tool is recommended. However, if you plan to use it as a GUI testing tool, be aware that its current activity coverage may not be accurate since the possible false positive crashes.

I will find a slot to release a version that corresponds to the TOSEM paper after finishing my phd thesis. 

If this tool benifits your work, we hope you cite our paper.


@article{hu2024enhancing,

  title={Enhancing GUI Exploration Coverage of Android Apps with Deep Link-Integrated Monkey},
  
  author={Hu, Han and Wang, Han and Dong, Ruiqi and Chen, Xiao and Chen, Chunyang},
  
  journal={ACM Transactions on Software Engineering and Methodology},
  
  year={2024},
  
  publisher={ACM New York, NY}
  
}



# Guided Explore
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
 
