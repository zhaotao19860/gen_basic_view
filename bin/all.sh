#!/bin/bash
#Created by tom on 02/25/2019

# Exit immediately if a command exits with a non-zero status.
set -e

init(){ 
    SHELL_NAME=$0
    SHELL_FOLDER=$(dirname $(readlink -f "$0"))
    mkdir -p $SHELL_FOLDER/../log/
}

gen(){
    sh $SHELL_FOLDER/gen.sh
    echo "$(date) [$SHELL_NAME][$LINENO] [INFO] gen.sh success."
}

main(){
    init $@
    gen
}

main $@