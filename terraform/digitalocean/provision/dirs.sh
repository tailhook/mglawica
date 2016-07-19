# Terraform can't create dirs for some reason
# Even more, instead of creating a directory it writes the file with shortening
# the name


#mkdir /etc/cantal
mkdir /var/lib/cantal

#mkdir /etc/lithos
mkdir /var/lib/lithos
mkdir /var/log/lithos
mkdir /var/lib/lithos/images
chown rsyncd /var/lib/lithos/images
mkdir /etc/lithos/sandboxes
mkdir /etc/lithos/processes

mkdir /etc/verwalter
mkdir /var/lib/verwalter
mkdir /var/log/verwalter
mkdir /etc/verwalter/runtime
mkdir /etc/verwalter/scheduler
mkdir /etc/verwalter/templates
mkdir /etc/verwalter/templates/simple
mkdir /etc/verwalter/frontend

mkdir /etc/nginx/verwalter-configs
