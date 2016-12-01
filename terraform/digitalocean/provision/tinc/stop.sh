#!/bin/sh
pid=$(cat /tmp/tinc.mglawica.pid)
[ -n "$pid" ] && kill $pid
