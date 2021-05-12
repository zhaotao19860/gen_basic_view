#!/bin/bash
#  Created by tom on 02/22/2019

# Exit immediately if a command exits with a non-zero status.
set -e

SHELL_FOLDER=$(dirname $(readlink -f "$0"))

build(){
    pyinstaller -F $SHELL_FOLDER/gen_map.py
    pyinstaller -F $SHELL_FOLDER/ipv4_format.py
    pyinstaller -F $SHELL_FOLDER/ipv4_new.py
    pyinstaller -F $SHELL_FOLDER/ipv4_merge.py
    pyinstaller -F $SHELL_FOLDER/ipv6_format.py
    pyinstaller -F $SHELL_FOLDER/ipv6_new.py
    pyinstaller -F $SHELL_FOLDER/ipv6_merge.py

    cp $SHELL_FOLDER/dist/* $SHELL_FOLDER/
    \rm -rf $SHELL_FOLDER/dist 
    \rm -rf $SHELL_FOLDER/build 
    \rm -rf $SHELL_FOLDER/*.spec
}

main(){
    build
}

main

