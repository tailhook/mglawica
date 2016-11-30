#!/bin/sh -e
: ${VAGGA:-vagga}
[ -d dist ] || mkdir dist
$VAGGA _pack_image -J package > dist/barnard-dev.tar.xz
sum=$(sha256sum dist/barnard-dev.tar.xz | cut -d' ' -f1)
cat <<END
- !Tar
  url: http://localhost:8000/barnard-dev.tar.xz
  sha256: $sum
END
