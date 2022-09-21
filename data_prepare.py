import os
import random
from utils.group import Groups
import definitions
import threading


def remove_files(dir):
    for entry in os.scandir(dir):
        if entry.is_dir():
            remove_files(entry)
        else:
            os.remove(entry)


def split(g, i, len_gs, out):
    print(g)
    if i < (len_gs * 0.9):
        print("to train")
        p, t = g.wireframe("leaf", "split")
        pout = os.path.join(out, "A", "train", f"{g.id}.png")
        tout = os.path.join(out, "B", "train", f"{g.id}.png")
        p.save(pout)
        t.save(tout)
    else:
        print("to test")
        p, t = g.wireframe("leaf", "split")
        pout = os.path.join(out, "A", "test", f"{g.id}.png")
        tout = os.path.join(out, "B", "test", f"{g.id}.png")
        p.save(pout)
        t.save(tout)


def merge(g, i, len_gs, out):
    print(g)
    p, t = g.wireframe("leaf", "split")
    if i < (len_gs * 0.9):
        print("to train")
        path_a = os.path.join("train", f"{g.id}_A.png")
        path_b = os.path.join("train", f"{g.id}_B.png")
        p.save(os.path.join(out, path_a))
        t.save(os.path.join(out, path_b))
        train_list = os.path.join(out, "pix2pix_train_list")
        with open(train_list, "a+") as f:
            f.write(f"{path_a}\t{path_b}\n")
    else:
        print("to test")
        path_a = os.path.join("test", f"{g.id}_A.png")
        path_b = os.path.join("test", f"{g.id}_B.png")
        p.save(os.path.join(out, path_a))
        t.save(os.path.join(out, path_b))
        test_list = os.path.join(out, "pix2pix_test_list")
        with open(test_list, "a+") as f:
            f.write(f"{path_a}\t{path_b}\n")

def main():
    csv_path = "/run/media/di/HHD0/codes/UIAutomation/uiautomator2/results/results.csv"
    # out = "/home/di/Documents/FIT4441/pytorch-CycleGAN-and-pix2pix/datasets/androidui/"
    out = "/home/di/Documents/FIT4441/guidedExplore/data/uiauto/"
    remove_files(out)
    gs = Groups.from_scv(csv_path)
    gs.extend(Groups.from_out_dir(definitions.FILTERED_DIR))
    # gs = gs[:10]
    random.shuffle(gs)
    threads = [
        threading.Thread(target=merge, args=(g, i, len(gs), out))
        for i, g in enumerate(gs)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # asyncio.run(main())
    main()
