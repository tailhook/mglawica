#!/bin/sh -e
: ${VAGGA:=vagga}
version=$(git describe)
mkdir -p dist
$VAGGA _pack_image -J package > dist/barnard-${version}.tar.xz
url="http://sh.mglawica.org/barnard-images/barnard-${version}.tar.xz"
sum=$(sha256sum dist/barnard-${version}.tar.xz | cut -d' ' -f1)
sed '/url:/{s@http:.*@'$url'@};/sha256:/{s@\w.*@sha256: '$sum'@}' \
    bootstrap.sh  > dist/barnard-testing.sh
