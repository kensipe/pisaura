#!/usr/bin/env bash

# this failure script will produced at the tested host

if [[ "$1" == *revert* ]]
then
    echo "Revert service"
    sudo iptables-save | grep -v "remove_me" | sudo iptables-restore
else
    echo "Make failure"
    sudo iptables -A INPUT -m comment --comment "remove_me" -p tcp --destination-port $1 -j DROP
    sudo iptables -A OUTPUT -m comment --comment "remove_me" -p tcp --destination-port 2181 -j DROP
fi
