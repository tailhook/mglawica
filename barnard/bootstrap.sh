#!/bin/sh
VAGGA="${VAGGA:-vagga}"
DIR="$(pwd)"

fail() { echo "$*"; exit 1; }

type "$VAGGA" || fail "No vagga binary found"
type mktemp || fail "No mktemp binary found"

stat -t vagga.yaml || fail "File vagga.yaml not found in current dira"

set -e

tmpdir=$(mktemp -d)
trap "cd $tmpdir; vagga _clean --everything 2> /dev/null; cd /; rm -rf $tmpdir" EXIT

mkdir -p "$tmpdir/target/vagga"
cp vagga.yaml "$tmpdir/target/vagga.yaml"

cat <<END > "$tmpdir/vagga.yaml"
containers:
  barnard:
    setup:
    - !Tar
      url: http://localhost:8000/barnard-dev.tar.xz
      sha256: 030d372157bb2fbd38c12de1318f01908c435426d5c47fae9ce97b88e947a624

commands:
  barnard: !Command
    description: Run barnard (a container deployment tool)
    container: barnard
    run:
    - barnard
END

cd "$tmpdir"

"$VAGGA" barnard inject -f target/vagga.yaml

cd "$tmpdir/target"

"$VAGGA" _list | grep -q ^barnard$ || fail "Failed adding barnard command"
"$VAGGA" _list --containers | grep -q ^barnard$ || fail "Failed adding barnard container"

echo Ready. Copying files...

cp vagga.yaml "$DIR/vagga.yaml"
mkdir -p "$DIR/vagga"
cp vagga/* "$DIR/vagga"

cd "$DIR"

echo 'Running `vagga barnard bootstrap` you may do this at any time'

"$VAGGA" barnard bootstrap || fail "Something wrong during bootstrap. You may wish to run it again (or use git)"

echo 'Fine. You may want to `git commit` now'
