
def count_method(log):
    method = set()
    onclick = set()
    with open(log, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for line in lines:
            if 'System.out:' in line:
                line = line.strip()
                tag = int(line.split()[-1])
                if 'method' in line:
                    method.add(tag)
                if 'onclick' in line:
                    onclick.add(tag)

    print('methods: ', len(method))
    print('onclick: ', len(onclick))


if __name__ == '__main__':
    log = r'../data/rq3/fastbot/fastbot_nosurffirreddit.txt'
    count_method(log)