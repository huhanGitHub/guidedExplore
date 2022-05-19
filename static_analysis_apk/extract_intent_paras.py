import os
import json
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
intent_smali_fileds = 'Landroid/content/Intent;->get'
intent_get_action = 'Landroid/content/Intent;->getAction()'
const_string = 'const-string'
package_identifier = 'package="'
equals_smali = 'Ljava/lang/String;->equals'
contains_smali = 'Ljava/util/Set;->contains'


# first check the field contains_smali and equals_smali to judge if equals or contains is existed
def check_equals_contains(smali_file):
    equals = False
    contains = False
    with open(smali_file, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            if equals_smali in line:
                equals = True
            if contains_smali in line:
                contains = True

    return equals, contains


def extract_force_test_strings(smali_file):
    strings = []
    equals, contains = check_equals_contains(smali_file)
    if equals or contains:
        # extract all strings
        with open(smali_file, 'r+', encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                if const_string in line:
                    tag = line.strip()
                    tag = tag[tag.index('"') + 1: tag.rindex('"')]
                    tag = tag.replace('\n', '')
                    if tag != '':
                        strings.append(tag)

        if len(strings) != 0:
            if contains and not equals:
                strings = [' '.join(strings)]

            return strings

    return strings


# statistics intent paras
def intent_field_extractor(path):
    log = r'intent_smali_analysis.txt'
    fields = {}
    with open(log, 'a+', encoding='utf8') as log:
        for root, dirs, files in os.walk(path):
            for file in files:
                if str(file).endswith('smali'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r+', encoding='utf8') as f:
                        lines = f.readlines()
                        for line in lines:
                            if intent_smali_fileds in line:
                                index = line.index(intent_smali_fileds)
                                end = line.index('(', index)
                                field = line[index:end]
                                field = field.replace(';\n', '')
                                field = field.replace('Landroid/content/Intent;->', '')
                                counts = fields.setdefault(field, 0)
                                counts += 1
                                fields[field] = counts

        fields = sorted(fields.items(), key=lambda d: d[1], reverse=True)
        for k, v in fields:
            log.write(k + ' ' + str(v) + '\n')


def smali_intent_para_extractor(path, save_path):
    apps_intent_para = {}
    apps = [i for i in os.listdir(path)]

    # find package names for each app. find all activity names
    packages = []
    apps_activities = {}
    for app in apps:
        app_path = os.path.join(path, app)
        if not os.path.isdir(app_path):
            continue
        activities = []
        for file in os.listdir(app_path):
            if 'AndroidManifest.xml' in file:
                file_path = os.path.join(app_path, file)
                if 'original' in file_path:
                    continue
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    package = root.attrib.get('package', None)
                    if package is None:
                        continue
                    for node in root.iter('activity'):
                        name = node.attrib.get('{http://schemas.android.com/apk/res/android}name')
                        print('name ' + node.attrib.get('{http://schemas.android.com/apk/res/android}name'))
                        activities.append(name)
                except ET.ParseError as e:
                    print(str(e))
                    print(file_path)
                    package = file

                packages.append(package)
                apps_activities[package] = activities

    for app in apps:
        if ('.DS_Store' in app) or ('R.smali' in app):
            apps.remove(app)

    for subscript, app in enumerate(apps):
        app_path = os.path.join(path, app)
        intent_para = {}
        package = packages[subscript]
        for root, dirs, files in os.walk(app_path):
            for file in files:
                # use suffix 'activity' to judge
                if 'activity' in file or 'Activity' in file:
                    if file.endswith('.smali'):
                        file_path = os.path.join(root, file)
                        pairs = []
                        with open(file_path, 'r+', encoding='utf8') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if intent_smali_fileds in line:
                                    index = line.index(intent_smali_fileds)
                                    end = line.index('(', index)
                                    field = line[index:end]
                                    field = field.replace(';\n', '')
                                    field = field.replace('Landroid/content/Intent;->', '')

                                    # find const string in the previous lines
                                    pre_index = i - 1
                                    while pre_index >= 0:
                                        temp = lines[pre_index]
                                        if const_string in lines[pre_index]:
                                            tag = lines[pre_index].strip()
                                            tag = tag[tag.index('"') + 1: tag.rindex('"')]
                                            tag = tag.replace('\n', '')
                                            pair = [tag, field]
                                            pairs.append(pair)
                                            # print(temp)
                                            break
                                        else:
                                            pre_index = pre_index - 1

                            if len(pairs) != 0:
                                # handle anonymous functions in an activity
                                if '$' in file:
                                    file = file.split('$')[0]

                                file = file.replace('.smali', '')

                                # find the full name of activity
                                full_name_activities = apps_activities.get(package)
                                for full in full_name_activities:
                                    if file in full:
                                        file = full

                                cur_pairs = intent_para.setdefault(file, [])
                                cur_pairs.extend(pairs)
                                intent_para[file] = cur_pairs

        apps_intent_para[package] = intent_para
    save_json = json.dumps(apps_intent_para, indent=4)
    with open(save_path, 'w', encoding='utf8') as f2:
        f2.write(save_json)


if __name__ == '__main__':
    # path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/recompile samples'
    # intent_field_extractor(path)
    path = r'../data/recompiled_apks'
    save_path = r'../data/intent_para.json'
    smali_intent_para_extractor(path, save_path)