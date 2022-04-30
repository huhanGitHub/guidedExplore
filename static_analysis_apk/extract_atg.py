import os
import re
import json


def activity_mapping(abs_path, folders, available_activity_dict, save_dir=r'activity_match'):
    for folder in folders:
        activity_dict = {}
        folder_path = os.path.join(abs_path, folder)
        os.chdir(folder_path)
        smali_folders = os.listdir()
        smali_folders = [x for x in smali_folders if 'smali' in x]

        count = 0
        print('@@@@@@@@@@@@@@@@@@@@@@   ' + folder + '   @@@@@@@@@@@@@@@@@@@@@@')
        # print(avaliable_activity_dict[folder])
        for smali_folder in smali_folders:
            # print(smali_folder)
            smali_path = os.path.join(folder_path, smali_folder)
            os.chdir(smali_path)
            # print(os.listdir())
            for root, dirs, files in os.walk('.'):
                # print(dirs)
                for file in files:

                    # if ("$" in file) or ('.DS_Store' in file) or ('R.smali' in file):
                    #     continue
                    if ('.DS_Store' in file) or ('R.smali' in file):
                        continue

                    fullpath = os.path.join(root, file)
                    activity_lst = []
                    # class_path = fullpath[2:].replace('/', '.')
                    class_path = fullpath[2:][:-6]
                    # print(fullpath)
                    try:
                        with open(fullpath, 'r') as f:
                            print("!!!!!!!!!!!!!")
                            # print(file)
                            lines = f.readlines()
                            # print(lines)
                            file_length = len(lines)

                            for line_index in range(file_length):
                                current_line = lines[line_index]

                                if 'setClassName' in current_line:
                                    for callback_index in range(line_index, line_index - 10, -1):
                                        lastLine = lines[callback_index]

                                        if 'const-string' in lastLine:
                                            activity = lastLine.split()[-1].replace("/", ".")
                                            if '$' in activity:
                                                activity = activity.split("$")[0]

                                            # print("____________")
                                            # print(activity)
                                            activity_lst.append(activity)

                                            # print(avaliable_activity_dict[folder])
                                            if activity in available_activity_dict[folder]:
                                                activity_lst.append(activity)
                                                print("!!!!!!!!")
                                                # print(activity)
                                                count += 1

                                if 'const-class' in current_line:
                                    activity = current_line.split()[-1][:-1][1:].replace("/", ".")
                                    if '[' in activity:
                                        continue
                                    if activity == class_path:
                                        continue

                                    if '$' in activity:
                                        activity = activity.split("$")[0]

                                    # print("!!!!!!!!!!!")
                                    # print(activity)
                                    # activity_lst.append(activity)

                                    if activity in available_activity_dict[folder]:
                                        activity_lst.append(activity)
                                    # print(activity)
                                    count += 1
                                # if len(activity) == 0:
                                #     activity_lst.remove(activity)

                            if activity_lst != [""] and len(activity_lst) != 0:
                                # print(class_path)
                                # print(activity_lst)
                                if "$" in class_path:
                                    class_path = class_path.split("$")[0]

                                if class_path in activity_dict.keys():
                                    activity_dict[class_path].extend(list(set(activity_lst)))
                                    activity_dict[class_path] = list(set(activity_dict[class_path]))
                                activity_dict[class_path] = list(set(activity_lst))
                    except Exception as e:
                        print(str(e))
                        # print(fullpath)
                        pass

            # Breaking for test
            # break
        for k, v in activity_dict.items():
            print(k, v)

        save_path = os.path.join(save_dir, folder + '.json')
        with open(save_path, 'w') as fp:
            json.dump(activity_dict, fp, indent=4)
            print('Count: ' + str(count))


def activity_searching(folders, abs_path):
    count = 0
    activity_dict = {}
    activity_lst = []

    print(folders)

    for folder in folders:
        # print(folder)
        folder_path = os.path.join(abs_path, folder)
        # os.chdir(folder_path)
        #        destination = '/Users/ruiqidong/Desktop/same-launcher/'
        #         print(folder)
        manifestval_path = os.path.join(folder_path, 'AndroidManifest.xml')
        # print('@@@@@@@@@@@@@@@@@@@@@@   ' + folder + '   @@@@@@@@@@@@@@@@@@@@@@')

        try:
            with open(manifestval_path, 'r', encoding='utf8') as file:
                lines = file.readlines()
                lines_length = len(lines)

                for line in lines:
                    m = re.match('.*<activity.*android:name=\"(.*)\".*>', line)
                    if m:
                        if len(m.group(1).split()) > 1:
                            activity = m.group(1).split()[0][:-1]
                        else:
                            activity = m.group(1)

                        # print(activity)
                        activity_lst.append(activity)

                #                for line_index in range(lines_length):
                #                    current_line = lines[line_index]
                #
                ##                        break
                activity_dict[folder] = list(set(activity_lst))
        except Exception as e:
            print(str(e))
            print(folder)
    # print(activity_dict)
    return activity_dict


def batch_extract(decompiled_apks, save_dir):
    # abs_path = '/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/data'
    folders = os.listdir(decompiled_apks)
    ignore = ['.idea', '.git', 'activity_match', 'README.md', '.DS_Store', '.ipynb_checkpoints', 'activity.py',
              'smalianalysis.py', 'activity.py', 'extract_atg.py']
    folders = [x for x in folders if x not in ignore]

    available_activity_dict = activity_searching(folders, decompiled_apks)

    # save_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/ATG/activity_match/atg'
    activity_mapping(decompiled_apks, folders, available_activity_dict, save_dir=save_dir)


def unit_extract(decompiled_apks, folder, available_activity_dict, save_dir=r'activity_match'):
    activity_dict = {}
    folder_path = os.path.join(decompiled_apks, folder)
    # os.chdir(folder_path)
    smali_folders = os.listdir(folder_path)
    smali_folders = [x for x in smali_folders if 'smali' in x]
    count = 0
    print('@@@@@@@@@@@@@@@@@@@@@@   ' + folder + '   @@@@@@@@@@@@@@@@@@@@@@')
    # print(avaliable_activity_dict[folder])
    for smali_folder in smali_folders:
        # print(smali_folder)
        smali_path = os.path.join(folder_path, smali_folder)
        # os.chdir(smali_path)
        for root, dirs, files in os.walk(smali_path):
            # print(dirs)
            for file in files:

                # if ("$" in file) or ('.DS_Store' in file) or ('R.smali' in file):
                #     continue
                if ('.DS_Store' in file) or ('R.smali' in file):
                    continue

                fullpath = os.path.join(root, file)
                activity_lst = []
                # class_path = fullpath[2:].replace('/', '.')
                class_path = fullpath[: fullpath.rindex('.smali')]
                class_path = class_path.replace(smali_path, '').replace('/', '.')
                try:
                    with open(fullpath, 'r', encoding='utf8') as f:
                        # print(file)
                        lines = f.readlines()
                        file_length = len(lines)

                        for line_index in range(file_length):
                            current_line = lines[line_index]

                            if 'setClassName' in current_line:
                                for callback_index in range(line_index, line_index - 10, -1):
                                    lastLine = lines[callback_index]

                                    if 'const-string' in lastLine:
                                        activity = lastLine.split()[-1].replace("/", ".")
                                        if '$' in activity:
                                            activity = activity.split("$")[0]

                                        # print("____________")
                                        # print(activity)
                                        activity_lst.append(activity)

                                        # print(avaliable_activity_dict[folder])
                                        if activity in available_activity_dict[folder]:
                                            activity_lst.append(activity)
                                            print("!!!!!!!!")
                                            # print(activity)
                                            count += 1

                            if 'const-class' in current_line:
                                activity = current_line.split()[-1][:-1][1:].replace("/", ".")
                                if '[' in activity:
                                    continue
                                if activity == class_path:
                                    continue

                                if '$' in activity:
                                    activity = activity.split("$")[0]

                                # print("!!!!!!!!!!!")
                                # print(activity)
                                # activity_lst.append(activity)

                                if activity in available_activity_dict[folder]:
                                    activity_lst.append(activity)
                                # print(activity)
                                count += 1
                            # if len(activity) == 0:
                            #     activity_lst.remove(activity)

                        if activity_lst != [""] and len(activity_lst) != 0:
                            # print(class_path)
                            # print(activity_lst)
                            if "$" in class_path:
                                class_path = class_path.split("$")[0]

                            if class_path in activity_dict.keys():
                                activity_dict[class_path].extend(list(set(activity_lst)))
                                activity_dict[class_path] = list(set(activity_dict[class_path]))
                            activity_dict[class_path] = list(set(activity_lst))
                except Exception as e:
                    print(str(e))
                    pass
        # break
    # for k,v in activity_dict.items():
    #     print(k,v)

    save_path = os.path.join(save_dir, folder + '.json')
    with open(save_path, 'a') as fp:
        json.dump(activity_dict, fp, indent=4)
        print('Count: ' + str(count))


if __name__ == '__main__':
    # decompiled_apks = '/Users/hhuu0025/PycharmProjects/guidedExplorer/data/recompiled_apks'
    # save_dir = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/activity_atg'

    decompiled_apks = '/Users/han/GoogleDrive/Monash/project/guidedExplore/data/recompiled_apks'
    save_dir = '/Users/han/GoogleDrive/Monash/project/guidedExplore/data/activity_atg'
    batch_extract(decompiled_apks=decompiled_apks, save_dir=save_dir)
