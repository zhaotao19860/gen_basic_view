#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Created by tom on 02/11/2019

###############################################################################
# 功能：
#     1.将new_ipv6_range.temp中viewid相同的地址段合并，输出到merged_ipv6_range.temp；
# 输入：
#     1.new_ipv6_range.temp
#       格式：
#       ip地址段        视图ID
#       2400:fdc0::/32	31
# 输出：
#     1.merged_ipv6_range.temp
#       格式：
#       ip地址段        视图ID
#       2400:fdc0::/32	31
###############################################################################

import sys
import os
import codecs
import logging
from intervaltree import Interval, IntervalTree
from netaddr import IPRange, IPNetwork, IPAddress
import traceback


def printUsage():
    print("Usage: python ./ipv6_merge.py\n")
    sys.exit(1)


def sort_and_merge(tree):
    """
    Finds all intervals with overlapping ranges and 
    data is the same and merges theminto a single 
    interval. 

    Completes in O(n*logn).
    """

    sorted_intervals = sorted(tree)  # get sorted intervals
    merged = []
    # use mutable object to allow new_series() to modify it
    higher = None  # iterating variable, which new_series() needs access to

    def new_series():
        merged.append(higher)
        return

    for higher in sorted_intervals:
        if merged:  # series already begun
            lower = merged[-1]
            if (higher.begin <= lower.end and
                    higher.data == lower.data):  # should merge
                upper_bound = max(lower.end, higher.end)
                merged[-1] = Interval(lower.begin,
                                      upper_bound, higher.data)
            else:
                new_series()
        else:  # not merged; is first of Intervals to merge
            new_series()

    return merged


def iprange_insert(tree, cidrip, view_id):
    ip = IPNetwork(cidrip)
    new_it = Interval(ip.first, ip.last + 1, view_id)
    try:
        conflicts = tree.overlap(ip.first, ip.last + 1)
        if len(conflicts):
            tree.remove_overlap(ip.first, ip.last + 1)
            for it in conflicts:
                logging.info("cidr[%s], id[%s] conflict with cidr[%s], id[%s]",
                             cidrip, view_id, IPRange(it.begin, it.end).cidrs(), it.data)
                if new_it.contains_interval(it) or new_it.range_matches(it):
                    continue
                elif it.contains_interval(new_it):
                    if new_it.begin == it.begin:
                        tree.addi(new_it.end, it.end, it.data)
                    elif new_it.end == it.end:
                        tree.addi(it.begin, new_it.begin, it.data)
                    else:
                        tree.addi(it.begin, new_it.begin, it.data)
                        tree.addi(new_it.end, it.end, it.data)
                elif new_it.ge(it):
                    tree.addi(it.begin, new_it.begin, it.data)
                elif new_it.le(it):
                    tree.addi(new_it.end, it.end, it.data)
        tree.add(new_it)
    except Exception:
        logging.error("traceback.format_exc():%s", traceback.format_exc())
        sys.exit(1)


def merge_new_range_file(new_range_file_name, merged_range_file_name):
    tree = IntervalTree()
    try:
        with codecs.open(new_range_file_name, 'r', 'UTF-8') as fr:
            for line in fr:
                line = line.strip()
                # 跳过注释行和空行
                if not len(line) or line.startswith('#'):
                    continue
                tmp = line.split()
                # ip     视图ID
                # tmp[0] tmp[1]
                iprange_insert(tree, tmp[0], tmp[1])
        merged = sort_and_merge(tree)
        with codecs.open(merged_range_file_name, 'a', 'UTF-8') as fm:
            fm.seek(0)
            fm.truncate()
            for interval_obj in merged:
                begin, end, data = interval_obj
                ip = IPRange(str(IPAddress(begin, 6)), end - 1)
                for cidr in ip.cidrs():
                    fm.writelines([str(cidr), '    ', data, '\n'])
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
    log = script_path + '/../log/ipv6_merge.log'
    mk_dir(log)
    logging.basicConfig(filename=log, level=logging.INFO, filemode='a',
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s')
    logging.info('........run start........')
    new_range_file_name = script_path + "/../data/temp/new_ipv6_range.temp"
    mk_dir(new_range_file_name)
    merged_range_file_name = script_path + "/../data/temp/merged_ipv6_range.temp"

    merge_new_range_file(new_range_file_name, merged_range_file_name)


if __name__ == '__main__':
    main()
