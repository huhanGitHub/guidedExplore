import os
import logging

def create(dir):
    if not os.path.exists(dir):
        logging.info(f"Creating directory: {dir}")
        os.mkdir(dir)
    return dir


def basename_no_ext(path):
    """
    example: /x/y/z.apk return z
    """
    return os.path.basename((os.path.splitext(path)[0]))


def name_to_map(f):
    if type(f) is os.DirEntry:
        f = f.name
    f = basename_no_ext(f)
    [id, device, act, _] = f.split("_")
    return {"id": id, "device": device, "act": act}
