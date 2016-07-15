#!/bin/sh -ex
PROVISION_DIR=/vagrant/provision

echo "deb [trusted=yes] http://repo.mglawica.org xenial cantal-stable" \
| tee /etc/apt/sources.list.d/cantal.list

echo "deb [trusted=yes] http://repo.mglawica.org xenial verwalter-stable" \
| tee /etc/apt/sources.list.d/verwalter.list

echo "deb [trusted=yes] http://repo.mglawica.org xenial lithos-stable" \
| tee /etc/apt/sources.list.d/lithos.list

apt-get update
apt-get install -y cantal verwalter lithos rsync cgroup-lite nginx

adduser --system verwalter
adduser --system rsyncd

mkdir /etc/cantal
mkdir /var/lib/cantal

mkdir /etc/lithos
mkdir /var/lib/lithos
mkdir /var/log/lithos
lithos_mkdev /var/lib/lithos/dev
mkdir /var/lib/lithos/images
chown rsyncd /var/lib/lithos/images
mkdir /etc/lithos/sandboxes
mkdir /etc/lithos/processes
cp $PROVISION_DIR/lithos.master.yaml /etc/lithos/master.yaml

mkdir /etc/verwalter
mkdir /var/lib/verwalter
mkdir /var/log/verwalter
mkdir /etc/verwalter/runtime
mkdir /etc/verwalter/scheduler
mkdir /etc/verwalter/templates
mkdir /etc/verwalter/templates/simple
mkdir /etc/verwalter/frontend
chown verwalter /var/log/verwalter /var/lib/verwalter
cp -R $PROVISION_DIR/scheduler /etc/verwalter/scheduler/v1
cp -R $PROVISION_DIR/templates /etc/verwalter/templates/simple/v1
ln -s /usr/share/verwalter/frontend /etc/verwalter/frontend/common
cp $PROVISION_DIR/verwalter.sudoers /etc/sudoers.d/verwalter

cp $PROVISION_DIR/nginx.conf /etc/nginx
mkdir /etc/nginx/verwalter-configs
chown verwalter /etc/nginx/verwalter-configs

cp $PROVISION_DIR/rsyncd.conf /etc/rsyncd.conf
cp $PROVISION_DIR/cantal.service /etc/systemd/system/cantal.service
cp $PROVISION_DIR/lithos.service /etc/systemd/system/lithos.service
cp $PROVISION_DIR/verwalter.service /etc/systemd/system/verwalter.service

start cantal
start lithos
start verwalter
