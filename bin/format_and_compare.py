#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Created by tom on 02/20/2019

###############################################################################
# 功能：
#     1.比较新生成的文件与旧文件的差别，并已html格式展示，方便查看；
# 输入：
#     1.auto.view.map    //视图定义文件
#     2.view_name_id.map //视图-id对应文件
#     3.ip_range.map     //ipv4-视图对应文件
#     4.ipv6_range.map   //ipv6-视图对应文件
#     5.all              //所有文件
# 输出：
#     1.auto.view.map.diff.html    //视图定义文件差异
#     2.view_name_id.map.diff.html //视图-id对应文件差异
#     3.ip_range.map.diff.html     //ipv4-视图对应文件差异
#     4.ipv6_range.map.diff.html   //ipv6-视图对应文件差异
###############################################################################

import sys
import os
import codecs
import difflib
from netaddr import IPRange, IPNetwork, IPAddress, ZEROFILL
import logging
import traceback


def printUsage():
    logging.info(
        "Usage: python ./format_and_compare.py [view_name_id.map/ip_range.map/ipv6_range.map/all]")
    sys.exit(1)


def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError:
        print("ERROR: 没有找到文件:%s或读取文件失败！" % filename)
        sys.exit(1)


def compare_file(file1, file2, out_file):
    file1_content = read_file(file1)
    file2_content = read_file(file2)
    d = difflib.HtmlDiff()
    # 显示完整文件
    # result = d.make_file(file1_content, file2_content)
    # 只显示上下文差异
    result = d.make_file(file1_content, file2_content, fromdesc='',
                         todesc='', context=True, numlines=2)
    # 由于python2不支持指定编码，所以硬性将charset=ISO-8859-1替换为charset=UTF-8
    with open(out_file, 'w') as f:
        f.seek(0)
        f.truncate()
        for eachline in result:
            f.writelines(eachline.replace('charset=ISO-8859-1', 'charset=UTF-8'))


def get_view_dict_ip(view_map_file_name):
    view_dict = dict()
    try:
        with codecs.open(view_map_file_name, 'r', 'UTF-8') as fv:
            for line in fv:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                # 跳过国外及港澳台视图
                if 'view_northern_america' in line:
                    continue
                if 'view_latin_america' in line:
                    continue
                if 'view_oceania' in line:
                    continue
                if 'view_africa' in line:
                    continue
                if 'view_europe' in line:
                    continue
                if 'view_asia' in line:
                    continue
                if 'view_world' in line:
                    continue
                if 'view_hk_mo_tw' in line:
                    continue
                tmp = line.split()
                # 视图名称  视图ID
                # tmp[0]    tmp[1]
                key = int(tmp[1])
                assert view_dict.get(key) == None
                view_dict[key] = tmp[0]
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)
    return view_dict


def formate_view_map_file(in_file_name, out_file_name):
    # 提取出第一列(视图名称)及第三列(父视图名称),用于比较
    try:
        with codecs.open(in_file_name, 'r', 'UTF-8') as fr,\
                codecs.open(out_file_name, 'a', 'UTF-8') as fw:
            fw.seek(0)
            fw.truncate()
            for line in fr:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # 视图名称   视图ID    父视图名称
                # tmp[0]    tmp[1]    tmp[2]
                # 将ip地址格式转换为cidr格式
                if len(tmp) == 3:
                    fw.writelines([tmp[0], '\t', tmp[2], '\n'])
                else:
                    fw.writelines([tmp[0], '\n'])
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)


def formate_ipv4_file(in_file_name, out_file_name, view_map_file_name):
    # 将"ip_start ip_end view_id"格式转换为"view_name cidr"
    view_dict = get_view_dict_ip(view_map_file_name)
    try:
        with codecs.open(in_file_name, 'r', 'UTF-8') as fr,\
                codecs.open(out_file_name, 'a', 'UTF-8') as fw:
            fw.seek(0)
            fw.truncate()
            for line in fr:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # ip-start ip-end     视图ID
                # tmp[0]   tmp[1]     tmp[2]
                view_name = view_dict.get(int(tmp[2]))
                if view_name == None:
                    # 跳过不需要比较的视图
                    # logging.warn("cannot find view_name for view_id[%s] in [%s]",
                    #             tmp[2], view_map_file_name)
                    continue
                else:
                    ip = IPRange(tmp[0], tmp[1])
                    for cidr in ip.cidrs():
                        fw.writelines([view_name, '\t', str(cidr), '\n'])
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)


def formate_ipv6_file(in_file_name, out_file_name, view_map_file_name):
    # 将"ip_start ip_end view_id"格式转换为"view_name cidr"
    view_dict = get_view_dict_ip(view_map_file_name)
    try:
        with codecs.open(in_file_name, 'r', 'UTF-8') as fr,\
                codecs.open(out_file_name, 'a', 'UTF-8') as fw:
            fw.seek(0)
            fw.truncate()
            for line in fr:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # ip     视图ID
                # tmp[0] tmp[1]
                view_name = view_dict.get(int(tmp[1]))
                if view_name == None:
                    # 跳过不需要比较的视图
                    # logging.warn("cannot find view_name for view_id[%s] in [%s]",
                    #             tmp[1], view_map_file_name)
                    continue
                else:
                    fw.writelines([view_name, '\t', tmp[0], '\n'])
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)


def formate(file_path):
    formate_view_map_file(file_path + "/view_name_id.map",
                          file_path + "/view_name_id.map.format")
    formate_ipv4_file(file_path + "/ip_range.map",
                      file_path + "/ip_range.map.format",
                      file_path + "/view_name_id.map")
    formate_ipv6_file(file_path + "/ipv6_range.map",
                      file_path + "/ipv6_range.map.format",
                      file_path + "/view_name_id.map")


def compare(old_file_path, new_file_path, diff_file_path):
    compare_file(old_file_path + "/auto.view.map",
                 new_file_path + "/auto.view.map",
                 diff_file_path + "/auto.view.map.diff.html")
    compare_file(old_file_path + "/view_name_id.map.format",
                 new_file_path + "/view_name_id.map.format",
                 diff_file_path + "/view_name_id.map.diff.html")
    compare_file(old_file_path + "/ip_range.map.format",
                 new_file_path + "/ip_range.map.format",
                 diff_file_path + "/ip_range.map.diff.html")
    compare_file(old_file_path + "/ipv6_range.map.format",
                 new_file_path + "/ipv6_range.map.format",
                 diff_file_path + "/ipv6_range.map.diff.html")


def main():

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='')

    if len(sys.argv) != 2:
        printUsage()

    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    old_file_path = script_path + "/temp/old/"
    new_file_path = script_path + "/temp/new/"
    diff_file_path = script_path + "/temp/diff/"

    if "auto.view.map" in sys.argv[1]:
        compare_file(old_file_path + "/auto.view.map",
                     new_file_path + "/auto.view.map",
                     diff_file_path + "/auto.view.map.diff.html")
    elif "view_name_id.map" in sys.argv[1]:
        formate_view_map_file(old_file_path + "/view_name_id.map",
                              old_file_path + "/view_name_id.map.format")
        formate_view_map_file(new_file_path + "/view_name_id.map",
                              new_file_path + "/view_name_id.map.format")
        compare_file(old_file_path + "/view_name_id.map.format",
                     new_file_path + "/view_name_id.map.format",
                     diff_file_path + "/view_name_id.map.diff.html")
    elif "ip_range.map" in sys.argv[1]:
        formate_ipv4_file(old_file_path + "/ip_range.map",
                          old_file_path + "/ip_range.map.format",
                          old_file_path + "/view_name_id.map")
        formate_ipv4_file(new_file_path + "/ip_range.map",
                          new_file_path + "/ip_range.map.format",
                          new_file_path + "/view_name_id.map")
        compare_file(old_file_path + "/ip_range.map.format",
                     new_file_path + "/ip_range.map.format",
                     diff_file_path + "/ip_range.map.diff.html")
    elif "ipv6_range.map" in sys.argv[1]:
        formate_ipv6_file(old_file_path + "/ipv6_range.map",
                          old_file_path + "/ipv6_range.map.format",
                          old_file_path + "/view_name_id.map")
        formate_ipv6_file(new_file_path + "/ipv6_range.map",
                          new_file_path + "/ipv6_range.map.format",
                          new_file_path + "/view_name_id.map")
        compare_file(old_file_path + "/ipv6_range.map.format",
                     new_file_path + "/ipv6_range.map.format",
                     diff_file_path + "/ipv6_range.map.diff.html")
    elif "all" in sys.argv[1]:
        formate(old_file_path)
        formate(new_file_path)
        compare(old_file_path, new_file_path, diff_file_path)
    else:
        printUsage()


if __name__ == '__main__':
    main()
