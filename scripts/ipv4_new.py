#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Created by tom on 02/11/2019

###############################################################################
# 功能：
#     1.根据ipv4_format.temp和auto.view.map生成new_ip_range.temp；
# 输入：
#     1.ipv4_format.temp
#       格式：
#       ip地址段           国家  省份  运营商
#       4.4.4.0-4.4.4.255 中国	北京  移动
#     2.auto.view.map
#       格式：
#       视图名称      上级视图名称   所属搜索引擎/大洲/国家  所属省    所属运营商
#       view_default  none          none                   none     none
# 输出：
#     1.new_ip_range.temp
#       格式：
#       起始IP     终止IP     视图ID
#       1032389808 1032389823 151
###############################################################################

import sys
import os
import codecs
import logging
from netaddr import IPAddress, ZEROFILL
import traceback

def printUsage():
    print("Usage: python ./ipv4_new.py\n")
    sys.exit(1)

def get_view_dict_auto(view_map_file_name):
    view_dict = dict()
    id = 0
    try:
        with codecs.open(view_map_file_name, 'r', 'UTF-8') as fv:
            for line in fv:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # 视图名称  上级视图名称  所属国家/大洲  所属省   所属运营商
                # tmp[0]   tmp[1]       tmp[2]        tmp[3]  tmp[4]
                key = tmp[2] + '.' + tmp[3] + '.' + tmp[4]
                assert view_dict.get(key) == None
                view_dict[key] = id
                id = id + 1
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)
    return view_dict


def gen_new_range(format_file_name, view_map_file_name, out_file_name):
    view_dict = get_view_dict_auto(view_map_file_name)
    try:
        with codecs.open(format_file_name, 'r', 'UTF-8') as ff,\
                codecs.open(out_file_name, 'a', 'UTF-8') as fo:
            fo.seek(0)
            fo.truncate()
            for line in ff:
                tmp = line.split()
                # ip     国家    省份   运营商
                # tmp[0] tmp[1] tmp[2]  tmp[3]
                key = tmp[1] + '.' + tmp[2] + '.' + tmp[3]
                value = view_dict.get(key)
                if value == None:
                    logging.error("file[%s], %s, view id not exist",
                                  format_file_name, line)
                    sys.exit(1)
                else:
                    ip = tmp[0].split('-')
                    ip_start = int(IPAddress(ip[0], flags=ZEROFILL))
                    ip_end = int(IPAddress(ip[1], flags=ZEROFILL))
                    fo.writelines(
                        [str(ip_start), '\t', str(ip_end), '\t', str(value), '\n'])
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)


def get_path():
    path=os.path.dirname(os.path.realpath(sys.argv[0]))
    return path


def mk_dir(full_path):
    path=os.path.dirname(full_path)
    if not os.path.exists(path):
        os.mkdir(path)


def main():
    if len(sys.argv) != 1:
        printUsage()

    script_path=get_path()
    log=script_path + '/../log/ipv4_new.log'
    mk_dir(log)
    logging.basicConfig(filename=log, level=logging.INFO, filemode='a',
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s')
    logging.info('........run start........')
    format_file_name=script_path + "/../data/temp/ipv4_format.temp"
    mk_dir(format_file_name)
    view_map_file_name=script_path + "/../data/auto.view.map"
    new_range_file_name=script_path + "/../data/temp/new_ip_range.temp"

    gen_new_range(format_file_name, view_map_file_name, new_range_file_name)


if __name__ == '__main__':
    main()
