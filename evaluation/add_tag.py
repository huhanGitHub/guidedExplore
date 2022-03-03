import os


def add_tag(java_path, tag_index):
    tag_string = 'onClick('
    tag_index = tag_index
    package_name = 'import protect.card_locker.Milestone;\n'
    contents = ''
    with open(java_path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        contents = lines
        for index, line in enumerate(lines):
            if tag_string in line:
                cur_line = line
                cur_index = index
                # find { to insert code
                while '{' not in cur_line:
                    cur_index = cur_index + 1
                    cur_line = lines[cur_index]

                replace_string = '{' + '\n Milestone mile = new Milestone("point {0}"); \n mile.tag(); \n'.format(str(tag_index))
                cur_line = cur_line.replace('{', replace_string)
                tag_index += 1
                contents[cur_index] = cur_line

    contents.insert(1, package_name)
    with open(java_path, 'w', encoding='utf8') as f:
        f.writelines(contents)

    return tag_index


def add_tag_sysout_click(java_path, tag_index):
    tag_string = 'onClick('
    tag_index = tag_index
    contents = ''
    with open(java_path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        contents = lines
        for index, line in enumerate(lines):
            if tag_string in line:
                cur_line = line
                cur_index = index
                # find { to insert code
                while '{' not in cur_line:
                    cur_index = cur_index + 1
                    cur_line = lines[cur_index]

                replace_string = '{' + '\n java.lang.System.out.println("onclick {0}");  \n'.format(str(tag_index))
                cur_line = cur_line.replace('{', replace_string)
                tag_index += 1
                contents[cur_index] = cur_line

    # contents.insert(1, package_name)
    with open(java_path, 'w', encoding='utf8') as f:
        f.writelines(contents)

    return tag_index


def add_tag_sysout_all(java_path, tag_index):
    tag_strings = ['public ', 'boolean ', 'void ', 'String ', 'int ', 'float ', 'List<', 'private ']
    tag_index = tag_index
    contents = ''
    with open(java_path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        contents = lines
        for index, line in enumerate(lines):
            line = line.strip()
            status = False
            for tag in tag_strings:
                if line.startswith(tag):
                    status = True
                    break
            if status:
                if '(' in line and ')' in line and '{' in line:
                    cur_line = line
                    cur_index = index
                    # find { to insert code
                    while '{' not in cur_line:
                        cur_index = cur_index + 1
                        cur_line = lines[cur_index]

                    replace_string = '{' + '\n java.lang.System.out.println("method {0}");  \n'.format(str(tag_index))
                    cur_line = cur_line.replace('{', replace_string)
                    tag_index += 1
                    contents[cur_index] = cur_line

    # contents.insert(1, package_name)
    with open(java_path, 'w', encoding='utf8') as f:
        f.writelines(contents)

    return tag_index


def batch_add_tag(dir):
    tag_index = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            if str(file).endswith('.java'):
                file_path = os.path.join(root, file)
                tag_index = add_tag_sysout_all(file_path, tag_index)

    print(tag_index)


if __name__=='__main__':
    java_file = r'/Users/hhuu0025/AndroidStudioProjects/TextPad/app/src/main/java/com/maxistar/textpad/activities/EditorActivity.java'
    tag_index = 0
    dir = r'/Users/hhuu0025/PycharmProjects/guidedExplorer/data/source_code_apks/ipfs-lite-master'
    batch_add_tag(dir)