#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

init(){
    OUTPUT=$(pwd)/output
    mkdir -p ${OUTPUT}
}

build(){
    cp -rf bin data out scripts ${OUTPUT}
}

main(){
    init
    build
}

main