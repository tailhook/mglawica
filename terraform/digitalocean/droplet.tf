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
            "apt-get install -y cantal verwalter lithos rsync cgroup-lite nginx tinc",
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

            "mkdir /etc/tinc",
            "mkdir /etc/tinc/mglawica",
            "mkdir /etc/tinc/mglawica/hosts",
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

    # Setup a VPN

    provisioner "local-exec" {
        command = "[ -d tinc ] && rm -rf tinc; mkdir tinc tinc/.host1 tinc/hosts"
    }
    provisioner "local-exec" {
        command = "tincd -c tinc -K < /dev/null"
    }
    provisioner "local-exec" {
        command = "tincd -c tinc/.host1 -K < /dev/null"
    }
    provisioner "local-exec" {
        command = "{ echo Subnet = 172.24.0.254; cat tinc/rsa_key.pub; } > tinc/hosts/origin"
    }
    provisioner "local-exec" {
        command = "{ echo Subnet = 172.24.0.1; echo Address = ${digitalocean_droplet.main.ipv4_address}; cat tinc/.host1/rsa_key.pub; } > tinc/hosts/host1"
    }
    provisioner "local-exec" {
        command = "cp provision/tinc/* tinc"
    }

    provisioner "file" {
        source = "provision/tinc-host1/"
        destination = "/etc/tinc/mglawica"
    }
    provisioner "file" {
        source = "tinc/rsa_key.pub"
        destination = "/etc/tinc/mglawica/hosts/origin.pub"
    }
    provisioner "file" {
        source = "tinc/.host1/"
        destination = "/etc/tinc/mglawica"
    }

    provisioner "file" {
        source = "provision/tinc.service"
        destination = "/etc/systemd/system/tinc.service"
    }

    provisioner "remote-exec" {
        inline = [
            "chmod +x /etc/tinc/mglawica/tinc-up",
            "chmod o-r /etc/tinc/mglawica/rsa_key.priv",
            "{ echo Subnet = 172.24.0.254; cat /etc/tinc/mglawica/hosts/origin.pub; } > /etc/tinc/mglawica/hosts/origin",
            "{ echo Subnet = 172.24.0.1; cat /etc/tinc/mglawica/rsa_key.pub; } > /etc/tinc/mglawica/hosts/host1",
            "systemctl enable tinc.service",
            "systemctl start tinc.service",
            "systemctl restart tinc.service", # ???
        ]
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
