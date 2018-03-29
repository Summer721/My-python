#
import argparse
from pathlib import Path
import datetime
import stat

# -rwxr-xr-x   1 root root    7271 Sep 18  2017 import_data.py

def analysis_mode(number):
    lst = ['r', 'w', 'x', 'r', 'w', 'x', 'r', 'w', 'x']
    number = bin(number)[-9:]
    ret = ""
    for i, v in enumerate(number):
        if number[i] == '1':
            ret += lst[i]
        else:
            ret += '-'
    return ret


def lst_dirs(path_dir:str, details=False, human=False, all=False):
    path_dir = Path(path_dir)

    def _analysis_time(path_obj:Path):
        access_time = path_obj.stat().st_atime
        tm = datetime.datetime.fromtimestamp(access_time).strftime('%Y-%m-%d %H:%M:%S')
        return tm

    for file_name in path_dir.iterdir():
        if not all and str(file_name.name).startswith('.'):
            continue
        if details:
            yield analysis_mode(file_name.stat().st_mode),_analysis_time(file_name),file_name.name
        else:
            yield file_name.name

parser = argparse.ArgumentParser(prog='ls', add_help=False)
parser.add_argument('path',nargs='?',default='.')
parser.add_argument('-l', '--list', action='store_true')
parser.add_argument('-a', '--all', action='store_true')
parser.add_argument('-h', '--human', action='store_true')


if __name__ == '__main__':
    args = parser.parse_args(('F:/Packages',))
    for file in lst_dirs(args.path, args.list, args.human, args.all):
        print(file)
