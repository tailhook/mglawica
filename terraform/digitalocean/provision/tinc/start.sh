#!/bin/sh
cfgdir=$(realpath $(dirname $0))
pidfile=/tmp/tinc.mglawica.pid
pid=$(cat $pidfile)
[ -n "$pid" ] && kill $pid 2>/dev/null

echo
echo 'We are going to start "tinc" a VPN daemon that will connect you'
echo 'securely to your cluster. This requires "sudo" access.'
echo

sudo tincd -c $cfgdir -U $USER --pidfile=$pidfile

echo
echo "Done. Now you can visit:"
echo "* http://h1.mglawica.org:8379/"
echo "* http://h1.mglawica.org:22682/"
echo "Or alternatively:"
echo "* http://172.24.0.1:8379/"
echo "* http://172.24.0.1:22682/"
echo "(note both access methods work only though VPN)"
echo "Next time you want to connect to VPN again run:"
echo "  ./tink/start.sh"
echo "from current directory"

