import os


def basename_no_ext(path):
    """
    example: /x/y/z.apk return z
    """
    return os.path.basename((os.path.splitext(path)[0]))
