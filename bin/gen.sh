#!/bin/bash
#  Created by tom on 02/13/2019

# Exit immediately if a command exits with a non-zero status.
set -e

SHELL_FOLDER=$(dirname $(readlink -f "$0"))
SHELL_NAME=$0

init(){
    chmod a+x $SHELL_FOLDER/../scripts/*
    mkdir -p $SHELL_FOLDER/../data/backup/ipv4
    mkdir -p $SHELL_FOLDER/../data/backup/ipv6
    mkdir -p $SHELL_FOLDER/../data/temp
    mkdir -p $SHELL_FOLDER/../log/
    mkdir -p $SHELL_FOLDER/../out/history
}

#生成新的view_name_id.map
gen_new_map(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start gen new view_name_id.map ..."
    $SHELL_FOLDER/../scripts/gen_map 
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] gen new view_name_id.map success"
}

#规范化输入文件
formate_ipv4(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start format ipv4..."
    $SHELL_FOLDER/../scripts/ipv4_format
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] format ipv4 success"
}

#生成new_ip_range.temp
gen_new_range_ipv4(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start gen new_ip_range.temp ..."
    $SHELL_FOLDER/../scripts/ipv4_new
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] gen new_ip_range.temp success"
}

#生成新的ip_range.map
gen_range_ipv4(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start gen new ip_range.map ..."
    $SHELL_FOLDER/../scripts/ipv4_merge
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] gen new ip_range.map success"
}

#规范化输入文件
formate_ipv6(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start format ipv6..."
    $SHELL_FOLDER/../scripts/ipv6_format
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] format ipv6 success"
}

#生成new_ipv6_range.temp
gen_new_range_ipv6(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start gen new_ipv6_range.temp ..."
    $SHELL_FOLDER/../scripts/ipv6_new
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] gen new_ipv6_range.temp success"
}

#生成ipv6_range.map
gen_range_ipv6(){
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] start gen new ipv6_range.map ..."
    $SHELL_FOLDER/../scripts/ipv6_merge
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] gen new ipv6_range.map success"
}

md5_cmp_for_dir(){
    md5_for_1=`find $1 -type f -exec md5sum {} \; | sort -k 2 | md5sum | awk '{print $1}'`
    md5_for_2=`find $2 -type f -exec md5sum {} \; | sort -k 2 | md5sum | awk '{print $1}'`
    if [ x$md5_for_1 == x$md5_for_2 ]
    then
        echo 0
    else
        echo 1
    fi
}

gen_ipv4(){
    rc=`md5_cmp_for_dir $SHELL_FOLDER/../data/backup/ipv4 $SHELL_FOLDER/../data/ipv4`
    if [ $rc != 0 ]
    then 
        formate_ipv4
        gen_new_range_ipv4
        gen_range_ipv4
    else
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] ipv4 file not change."
    fi
}

gen_ipv6(){
    rc=`md5_cmp_for_dir $SHELL_FOLDER/../data/backup/ipv6 $SHELL_FOLDER/../data/ipv6`
    if [ $rc != 0 ]
    then 
        formate_ipv6
        gen_new_range_ipv6
        gen_range_ipv6
    else
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] ipv6 file not change."
    fi
}

md5_cmp(){
    md5_for_1=`md5sum $1 |awk '{print$1}'`
    md5_for_2=`md5sum $2 | awk '{print$1}'`
    if [ x$md5_for_1 == x$md5_for_2 ]
    then
        echo 0
    else
        echo 1
    fi
}

update(){
    current_date=$(date "+%Y%m%d%H%M%S")
    back_dir=$SHELL_FOLDER/../out/history/${current_date}
    
    rc=`md5_cmp $SHELL_FOLDER/../out/view_name_id.map $SHELL_FOLDER/../data/temp/view_name_id.temp`
    if [ $rc != 0 ]
    then
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] view_name_id.map changed."
        mkdir -p $back_dir
        \cp -f $SHELL_FOLDER/../out/view_name_id.map $back_dir
        \cp -f $SHELL_FOLDER/../data/temp/view_name_id.temp $SHELL_FOLDER/../out/view_name_id.map
    else
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] view_name_id.map not change."
    fi

    rc=`md5_cmp $SHELL_FOLDER/../out/ip_range.map $SHELL_FOLDER/../data/temp/merged_ip_range.temp`
    if [ $rc != 0 ]
    then
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] ip_range.map changed."
        mkdir -p $back_dir
        \cp -f $SHELL_FOLDER/../out/ip_range.map $back_dir
        \cp -f $SHELL_FOLDER/../data/temp/merged_ip_range.temp $SHELL_FOLDER/../out/ip_range.map
    else
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] ip_range.map not change."
    fi

    rc=`md5_cmp $SHELL_FOLDER/../out/ipv6_range.map $SHELL_FOLDER/../data/temp/merged_ipv6_range.temp`
    if [ $rc != 0 ]
    then
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] ipv6_range.map changed."
        mkdir -p $back_dir
        \cp -f $SHELL_FOLDER/../out/ipv6_range.map $back_dir
        \cp -f $SHELL_FOLDER/../data/temp/merged_ipv6_range.temp $SHELL_FOLDER/../out/ipv6_range.map
    else
        echo "$(date) [$SHELL_NAME][$LINENO] [INFO] ipv6_range.map not change."
    fi

    \cp -f $SHELL_FOLDER/../data/auto.view.map $SHELL_FOLDER/../out/auto.view.map
}

main(){
    init
    gen_new_map
    gen_ipv4
    gen_ipv6
    update
}

main
