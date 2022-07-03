import os


def add_tag(java_path, tag_index):
    tag_string = "onClick("
    tag_index = tag_index
    package_name = "import protect.card_locker.Milestone;\n"
    contents = ""
    with open(java_path, "r", encoding="utf8") as f:
        lines = f.readlines()
        contents = lines
        for index, line in enumerate(lines):
            if tag_string in line:
                cur_line = line
                cur_index = index
                # find { to insert code
                while "{" not in cur_line:
                    cur_index = cur_index + 1
                    cur_line = lines[cur_index]

                replace_string = (
                    "{"
                    + '\n Milestone mile = new Milestone("point {0}"); \n mile.tag(); \n'.format(
                        str(tag_index)
                    )
                )
                cur_line = cur_line.replace("{", replace_string)
                tag_index += 1
                contents[cur_index] = cur_line

    contents.insert(1, package_name)
    with open(java_path, "w", encoding="utf8") as f:
        f.writelines(contents)

    return tag_index


def add_tag_sysout_all(java_path, tag_index, onclick_index):
    tag_strings = [
        "public void",
        "public static void",
        "void",
        "private void",
        "public boolean ",
        "boolean ",
        "public String ",
        "String",
        "int ",
        "public int",
        "float ",
        "public float",
        "List<",
        "public List<",
    ]
    onlick_tag = "onClick("
    onclick_status = False
    tag_index = tag_index
    onclick_index = onclick_index
    contents = []
    with open(java_path, "r", encoding="utf8") as f:
        lines = f.readlines()
        contents = lines
        for index in range(len(lines)):
            line = lines[index]
            line = line.lstrip()
            status = False
            for tag in tag_strings:
                if line.startswith(tag):
                    status = True
                    break
            if status:
                if (
                    "(" in line
                    and ")" in line
                    and ";" not in line
                    and "=" not in line
                    and "abstract" not in line
                    and "}" not in line
                ):

                    # check onlick method
                    if onlick_tag in line:
                        onclick_status = True

                    cur_line = line
                    cur_index = index
                    # find { to insert code
                    while "{" not in cur_line and cur_index + 1 < len(lines):
                        # contents[cur_index] = cur_line
                        cur_index = cur_index + 1
                        cur_line = lines[cur_index]

                    if cur_index + 1 >= len(lines):
                        continue
                    # check super, skip super method
                    nextline = lines[cur_index + 1]
                    if "super(" in nextline:
                        cur_line = cur_line + nextline
                        contents[cur_index + 1] = ""
                    replace_string = (
                        'java.lang.System.out.println("method {0}");  \n'.format(
                            str(tag_index)
                        )
                    )
                    cur_line = cur_line + replace_string
                    tag_index += 1
                    if onclick_status:
                        replace_click_string = (
                            'java.lang.System.out.println("onclick {0}");  \n'.format(
                                str(onclick_index)
                            )
                        )
                        cur_line = cur_line + replace_click_string
                        onclick_index += 1
                        onclick_status = False
                    contents[cur_index] = cur_line

    # contents.insert(1, package_name)
    with open(java_path, "w", encoding="utf8") as f:
        f.writelines(contents)

    return tag_index, onclick_index


def batch_add_tag_all(dir):
    tag_index = 1
    onclick_index = 1
    for root, dirs, files in os.walk(dir):
        for file in files:
            if str(file).endswith(".java"):
                file_path = os.path.join(root, file)
                tag_index, onclick_index = add_tag_sysout_all(
                    file_path, tag_index, onclick_index
                )
                # print('cur methods: ', str(tag_index))
                # print('cur onclick methods: ', str(onclick_index))

    print("all methods: ", str(tag_index))
    print("onclick methods: ", str(onclick_index))


if __name__ == "__main__":
    java_file = r"/Users/xxx/AndroidStudioProjects/TextPad/app/src/main/java/com/maxistar/textpad/activities/EditorActivity.java"
    tag_index = 0
    dir = r"../data/source_code_apks/NoSurfForReddit-master"
    batch_add_tag_all(dir)
