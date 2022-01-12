import os
from decompile_apk import unit_decpmpile, batch_decompile
from static_analysis_apk.instrument_apk import unit_inject, unit_sign_APK, batch_inject, batch_sign_apks
from static_analysis_apk.extract_atg import unit_extract, batch_extract, activity_searching
from static_analysis_apk.extract_intent_paras import smali_intent_para_extractor


def unit_run_preprocess(app_save_dir, repackage_app_save_dir, deeplinks_path, save_dir, recompiled_apks):
    if not os.path.exists(app_save_dir):
        print(app_save_dir, 'not found')
        return

    # # recompile apk
    # print('recompile', apk_path)
    # unit_decpmpile(apk_path, app_save_dir)

    # instrument apk
    apk = app_save_dir[app_save_dir.rindex('/') + 1:]
    repackage_app_save_apk = os.path.join(repackage_app_save_dir, apk)
    if not os.path.exists(repackage_app_save_apk):
        os.mkdir(repackage_app_save_apk)
    unit_inject(app_save_dir, repackage_app_save_apk, deeplinks_path)

    # extract atg
    folders = os.listdir(recompiled_apks)
    ignore = ['.idea', '.git', 'activity_match', 'README.md', '.DS_Store', '.ipynb_checkpoints', 'activity.py',
              'smalianalysis.py', 'activity.py']
    folders = [x for x in folders if x not in ignore]

    available_activity_dict = activity_searching(folders, recompiled_apks)
    folder = app_save_dir

    atg_save_dir = os.path.join(save_dir, 'activity_atg')
    if not os.path.exists(atg_save_dir):
        os.mkdir(atg_save_dir)
    unit_extract(decompiled_apks=recompiled_apks, folder=folder, available_activity_dict=available_activity_dict,
                 save_dir=atg_save_dir)

    # extract intent parameters
    # paras_save_path = os.path.join(save_dir, 'intent_para.json')
    # smali_intent_para_extractor(path=recompiled_apks, save_path=paras_save_path)


if __name__ == '__main__':
    app_save_dir = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/recompiled_apks/[PRODUCTIVITY]SendAnywher.apk'
    repackage_app_save_dir = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/repackaged_apks'
    deeplinks_path = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/unit_deeplinks.txt'
    save_dir = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data'
    recompiled_apks = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/recompiled_apks'
    unit_run_preprocess(app_save_dir, repackage_app_save_dir, deeplinks_path, save_dir, recompiled_apks)