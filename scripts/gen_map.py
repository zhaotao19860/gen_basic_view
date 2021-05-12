#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created by tom on 02/15/2019

###############################################################################
# 功能：
#     1.由auto.view.map生成view_name_id.temp；
# 输入：
#     1.auto.view.map
#       格式：
#       视图名称      上级视图名称   所属搜索引擎/大洲/国家  所属省    所属运营商
#       view_default  none          none                   none     none
# 输出：
#     1.view_name_id.temp
#       格式：
#       视图名称           视图ID  上级视图名称(可选)
#       view_default       0           
#       view_google_search 6       view_search 
###############################################################################

import sys
import codecs
import os
import traceback


def printUsage():
    print("Usage: python ./gen_map.py\n")
    sys.exit(1)

def gen_new_map_auto_id(view_file_name, new_map_file_name):
    id = 0
    try:
        with codecs.open(view_file_name, 'r', 'UTF-8') as fv,\
                codecs.open(new_map_file_name, 'a', 'UTF-8') as fn:
            fn.seek(0)
            fn.truncate()
            for line in fv:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # 视图名称 上级视图名称  所属国家/大洲  所属省   所属运营商
                # tmp[0]  tmp[1]       tmp[2]        tmp[3]  tmp[4]
                if 'none' in tmp[1]:
                    fn.writelines([tmp[0].ljust(30), str(id), '\n'])
                else:
                    fn.writelines([tmp[0].ljust(30), str(
                        id).ljust(10), tmp[1], '\n'])
                id = id + 1
    except Exception:
        print('traceback.format_exc():', traceback.format_exc())
        sys.exit(1)


def get_path():
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    return path


def mk_dir(full_path):
    path = os.path.dirname(full_path)
    if not os.path.exists(path):
        os.mkdir(path)


def main():
    if len(sys.argv) != 1:
        printUsage()

    script_path = get_path()

    view_file_name = script_path + "/../data/auto.view.map"
    new_map_file_name = script_path + "/../data/temp/view_name_id.temp"
    mk_dir(new_map_file_name)

    gen_new_map_auto_id(view_file_name, new_map_file_name)


if __name__ == '__main__':
    main()
