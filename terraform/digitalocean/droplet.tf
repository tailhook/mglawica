variable "do_token" {
    type = "string"
    description = "Digital Ocean API token"
}

variable "do_ssh_key" {
    type = "string"
    description = "Digital Ocean SSH Key"
}

provider "digitalocean" {
    token = "${var.do_token}"
}

resource "digitalocean_droplet" "main" {
    image = "ubuntu-16-04-x64"
    name = "mglawica-main-test"
    region = "fra1"
    size = "512mb"
    ssh_keys = ["${var.do_ssh_key}"]

    provisioner "file" {
        source = "provision/mglawica.list"
        destination = "/etc/apt/sources.list.d/mglawica.list"
    }

    provisioner "remote-exec" {
        inline = [
            "apt-get update",
            "apt-get install -y cantal verwalter lithos rsync cgroup-lite nginx",
            "adduser --system verwalter",
            "adduser --system rsyncd",

            # Terraform can't create dirs for some reason Even more, instead
            # of creating a directory it writes the file with shortening the
            # name
            "mkdir /etc/cantal",
            "mkdir /var/lib/cantal",

            "mkdir /etc/lithos",
            "mkdir /var/lib/lithos",
            "mkdir /var/log/lithos",
            "mkdir /var/lib/lithos/images",
            "chown rsyncd /var/lib/lithos/images",
            "mkdir /etc/lithos/sandboxes",
            "mkdir /etc/lithos/processes",
            "lithos_mkdev /var/lib/lithos/dev",

            "mkdir /etc/verwalter",
            "mkdir /var/lib/verwalter",
            "mkdir /var/log/verwalter",
            "mkdir /etc/verwalter/runtime",
            "mkdir /etc/verwalter/sandbox",
            "mkdir /etc/verwalter/scheduler",
            "mkdir /etc/verwalter/templates",
            "mkdir /etc/verwalter/frontend",

            "mkdir /etc/nginx/verwalter-configs",
        ]
    }


    provisioner "file" {
        source = "provision/lithos.master.yaml"
        destination = "/etc/lithos/master.yaml"
    }

    provisioner "file" {
        source = "provision/nginx.conf"
        destination = "/etc/nginx/nginx.conf"
    }

    provisioner "file" {
        source = "provision/rsyncd.conf"
        destination = "/etc/rsyncd.conf"
    }

    provisioner "file" {
        source = "provision/cantal.service"
        destination = "/etc/systemd/system/cantal.service"
    }

    provisioner "file" {
        source = "provision/lithos.service"
        destination = "/etc/systemd/system/lithos.service"
    }

    provisioner "file" {
        source = "provision/sudoers.txt"
        destination = "/etc/sudoers.d/verwalter"
    }


    provisioner "file" {
        source = "provision/verwalter.sandbox.yaml"
        destination = "/etc/verwalter/sandbox/log.yaml"
    }

    provisioner "file" {
        source = "provision/verwalter.service"
        destination = "/etc/systemd/system/verwalter.service"
    }

    provisioner "file" {
        source = "provision/scheduler"
        destination = "/etc/verwalter/scheduler/v1"
    }

    provisioner "file" {
        source = "provision/templates"
        destination = "/etc/verwalter/templates"
    }

    provisioner "remote-exec" {
        inline = [
            "systemctl enable cantal.service",
            "systemctl enable lithos.service",
            "systemctl enable verwalter.service",
            "systemctl enable rsync.service",
            "systemctl start cantal.service",
            "systemctl start lithos.service",
            "systemctl start verwalter.service",
            "systemctl start rsync.service",
        ]
    }

}
