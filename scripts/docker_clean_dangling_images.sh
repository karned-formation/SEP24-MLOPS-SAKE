#!/bin/bash
if [ -n "$(docker images -q -f dangling=true)" ]; then
    docker rmi $(docker images -q -f dangling=true) 
fi