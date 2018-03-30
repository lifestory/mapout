import os
import pathlib
class statics(object):
    def __init__(self):
        self.cur_dir = str(pathlib.Path.cwd().parent.as_posix())

        self.yaml_dir = self.cur_dir + '/spec'
        self.yaml_official = self.yaml_dir + '/official'

static_dirs = statics()

# if __name__ == '__main__':
#     print(static_dirs.yaml_dir)