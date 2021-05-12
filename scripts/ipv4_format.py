#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Created by tom on 02/11/2019

###############################################################################
# 功能：
#     1.将ipip.txtx格式化为统一格式，并输出到ipv4_format.temp；
#     2.将用户自定义文件格式化为统一格式，并输出到ipv4_format.temp；
# 输入：
#     1.ipip.txtx
#       格式：
#       起始ip           终止ip            国家   省   市  学校或单位  运营商  纬度       经度        所在时区代表城市  时区   中国行政区划代码 国际区号 国家代码 洲代码
#       001.000.008.000  001.000.015.255   中国  广东  *   *	      电信	 23.125178   113.280637  Asia/Shanghai   UTC+8  440000          86	     CN	     AP
#     2.user.xxxx(用户自定义文件)
#       IP地址段          所属搜索引擎/大洲/国家  所属省  所属运营商
#       1.1.1.1-2.2.2.2  日本                   none    none
#       4.4.4.0/24       中国	                北京	移动
# 输出：
#     1.ipv4_format.temp
#       格式：
#       ip地址段           国家  省份  运营商
#       4.4.4.0-4.4.4.255 中国	北京  移动
###############################################################################

from __future__ import unicode_literals
import sys
import os
import codecs
from netaddr import IPAddress, IPNetwork
import logging
import traceback

Reserved = ['保留地址', '本地地址', '局域网', '共享地址', '本机地址']
Internal = ['广州私网地址', '华北私网地址', '宿迁私网地址']
Continents = ['亚洲', '欧洲', '非洲', '北美洲', '南美洲', '大洋洲']
Searchs = ['yahoo', 'google', 'baidu', '360']
Countrys = ['美国', '阿根廷', '澳大利亚', '奥地利', '玻利维亚', '巴西', '柬埔寨', '加拿大', '智利', '哥伦比亚',
            '丹麦', '厄瓜多尔', '埃及', '英国', '芬兰', '法国', '希腊', '德国', '印度', '印度尼西亚',
            '意大利', '日本', '哈萨克斯坦', '韩国', '老挝', '马来西亚', '马尔代夫', '墨西哥', '缅甸', '尼泊尔',
            '荷兰', '新西兰', '挪威', '巴基斯坦', '巴拿马', '巴拉圭', '秘鲁', '菲律宾', '葡萄牙', '罗马尼亚',
            '俄罗斯', '沙特阿拉伯', '新加坡', '南非', '西班牙', '瑞典', '瑞士', '土耳其', '乌克兰', '阿联酋',
            '乌拉圭', '委内瑞拉', '越南', '泰国', '中国']

MainOperators = ['电信', '联通', '移动', '广电']
OtherOperators = ['电信通/长城', '教育网', '铁通', '方正', '华数', '中信网络', '东方有线',
                  '云创通讯', '网联光通', '友好联盟', '驰联', '蓝汛', '阿帕网络',
                  '光电创新', '昆时网络', '维实嘉业', '亿安天下','黑龙江广电','河南广电','方正网络',
                  '重庆广电']
BctvProvinces = ['山东','广东','内蒙古','重庆','贵州','宁夏','陕西','湖北']


def printUsage():
    print("Usage: python ./ipv4_format.py\n")
    sys.exit(1)


def walk_dir(dir_in, files_out):
    for root, _, files in os.walk(dir_in):
        for f in files:
            if f not in 'ipip.txtx':
                file_out = os.path.join(root, f)
                files_out.append(file_out)


def str_in_list(str_to_match, str_list):
    for elem in str_list:
        if elem in str_to_match:
            return elem
    return None


def str_not_in_list(str_to_match, str_list):
    for elem in str_list:
        if elem in str_to_match:
            return False
    return True


def str_in_list_exact(str_to_match, str_list):
    for elem in str_list:
        if elem == str_to_match:
            return elem
    return None


def str_not_in_list_exact(str_to_match, str_list):
    for elem in str_list:
        if elem == str_to_match:
            return False
    return True


def format_ipip(ipip_file_name, out_file_name):
    try:
        with codecs.open(ipip_file_name, 'r', 'UTF-8') as fr,\
                codecs.open(out_file_name, 'a', 'UTF-8') as fw:
            fw.seek(0)
            fw.truncate()
            for line in fr:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # ip-start  ip-end   国家    省份    地级市   学校或单位 运营商
                # tmp[0]    tmp[1]   tmp[2]  tmp[3]  tmp[4]  tmp[5]    tmp[6]
                # 保留地址
                if str_in_list(tmp[2], Reserved):
                    tmp[2] = '保留地址'
                    tmp[3] = tmp[6] = 'none'
                # 内部地址
                if str_in_list(tmp[2], Internal):
                    tmp[3] = tmp[6] = 'none'
                # 大洲地址
                if '亚太地区' in tmp[2]:
                    tmp[2] = '亚洲'
                    tmp[3] = tmp[6] = 'none'
                if '拉美地区' in tmp[2]:
                    tmp[2] = '南美洲'
                    tmp[3] = tmp[6] = 'none'
                if '欧洲地区' in tmp[2]:
                    tmp[2] = '欧洲'
                    tmp[3] = tmp[6] = 'none'
                if '非洲地区' in tmp[2]:
                    tmp[2] = '非洲'
                    tmp[3] = tmp[6] = 'none'
                if '北美地区' in tmp[2]:
                    tmp[2] = '北美洲'
                    tmp[3] = tmp[6] = 'none'

                # 将yahoo/baidu/google/360移到国家位置
                # 由于IPIP.txtx没有搜索引擎的IP特征，删除此处匹配
                # 如果需要配置，请在自定义文件user.xxxx中手动配置

                # 处理支持的国家
                if str_in_list_exact(tmp[2], Countrys) and '中国' not in tmp[2]:
                    tmp[3] = tmp[6] = 'none'
                # 处理不支持的国家
                if str_not_in_list_exact(tmp[2], Countrys + Searchs + Continents + Reserved + Internal):
                    tmp[2] = '海外线路'
                    tmp[3] = tmp[6] = 'none'
                # 处理港澳台
                if '香港' in tmp[3] or '澳门' in tmp[3] or '台湾' in tmp[3]:
                    tmp[6] = 'none'
                # 处理中国不支持的运营商
                if '中国' in tmp[2] and \
                    '香港' not in tmp[3] and \
                        '澳门' not in tmp[3] and \
                        '台湾' not in tmp[3]:
                    if str_not_in_list(tmp[6], MainOperators + OtherOperators):
                        tmp[3] = 'none'
                        tmp[6] = '其他运营商'
                # 处理四大运营商的省份信息及运营商信息
                mainoper = str_in_list(tmp[6], MainOperators)
                if mainoper:
                    if '中国' in tmp[3]:
                        tmp[3] = '其他'
                    if mainoper == '广电' and str_not_in_list(tmp[3], BctvProvinces):
                        tmp[3] = '其他'
                    tmp[6] = mainoper
                # 将包含省份信息的铁通归入相应省份的移动
                if '铁通' in tmp[6]:
                    if '中国' not in tmp[3]:
                        tmp[6] = '移动'
                # 处理第三方运营商的省份信息及运营商信息
                otheroper = str_in_list(tmp[6], OtherOperators)
                if otheroper:
                    tmp[3] = 'none'
                    tmp[6] = otheroper

                # 写入规范化文件
                fw.writelines([tmp[0], '-', tmp[1], '\t', tmp[2], '\t',
                               tmp[3], '\t', tmp[6], '\n'])
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)


def format_user(user_file_name, out_file_name):
    try:
        with codecs.open(user_file_name, 'r', 'UTF-8') as fu,\
                codecs.open(out_file_name, 'a', 'UTF-8') as fw:
            for line in fu:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # ip地址段 国家    省份   运营商
                # tmp[0]  tmp[1]  tmp[2] tmp[3]
                # 将ip地址格式转换为cidr格式
                if '-' in tmp[0]:
                    fw.writelines([tmp[0], '\t', tmp[1], '\t',
                                   tmp[2], '\t', tmp[3], '\n'])
                elif '/' in tmp[0]:
                    ip = IPNetwork(tmp[0])
                    ip_start = str(IPAddress(ip.first))
                    ip_end = str(IPAddress(ip.last))
                    # 写入规范化文件
                    fw.writelines([ip_start, '-', ip_end, '\t', tmp[1], '\t',
                                   tmp[2], '\t', tmp[3], '\n'])
                else:
                    logging.error("file[%s], %s\n, format error",
                                  user_file_name, line)
                    sys.exit(1)
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
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
    log = script_path + '/../log/ipv4_format.log'
    mk_dir(log)
    logging.basicConfig(filename=log, level=logging.INFO, filemode='a',
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s')
    logging.info('........run start........')
    ipip_file_name = script_path + "/../data/ipv4/ipip.txtx"
    mk_dir(ipip_file_name)
    format_file_name = script_path + "/../data/temp/ipv4_format.temp"
    mk_dir(format_file_name)
    data_dir = script_path + "/../data/ipv4/"
    user_file_names = []

    format_ipip(ipip_file_name, format_file_name)
    walk_dir(data_dir, user_file_names)
    # sort by suffix
    user_file_names.sort(key=lambda x: os.path.splitext(x)[-1][1:])
    for f in user_file_names:
        format_user(f, format_file_name)


if __name__ == '__main__':
    main()
