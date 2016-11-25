===========
Quick Start
===========

This is rough instruction at current point in time. We will make it
better, I promise!

For easy navigation we assume following folders:

* ``~/mglawica`` -- git checkout sources of this project
* ``~/foobar`` -- your project, which contains ``vagga.yaml``,
  which you want to deploy

Host dependencies:

* terraform_
* tinc_ (``apt-get install tinc``)
* vagga_ (from **testing** repo)

Supported hostings:

* `Digital Ocean`_

.. _terraform: https://www.terraform.io/downloads.html
.. _tinc: https://www.tinc-vpn.org/
.. _vagga: https://vagga.readthedocs.io/en/latest/installation.html

.. _Digital Ocean: https://digitalocean.com


Provision a Node
================

Tested with terraform == 0.6.15

Configuration of your account::

    cd terraform/digitalocean
    # create token in https://cloud.digitalocean.com/settings/api/tokens
    echo 'do_token = "xxxyour_tokenxx"' > key.tfvars
    # upload ssh key in https://cloud.digitalocean.com/settings/security
    echo 'do_ssh_key = "12:34:56:78:9a:bc:de:f1"' >> key.tfvars
    # optional public host (wildcard host should be configured)
    echo 'public_host = "my.host.whatever"' >> key.tfvars
    ./start.sh

This should ask your sudo password to connect to VPN, and finish with
following::

    Done. Now you can visit:
    * http://h1.mglawica.org:8379/
    * http://h1.mglawica.org:22682/
    Or alternatively:
    * http://172.24.0.1:8379/
    * http://172.24.0.1:22682/
    (note both access methods work only though VPN)
    Next time you want to connect o VPN again run:
      ./tink/start.sh
    from current directory

That's it for configuring VM. Note however that state is configured


Preparing a Project
===================


First insert ``barnard`` (our deployment tool) into your ``vagga.yaml``:

    cd ~/foobar
    mkdir vagga

    cat <<END > vagga/barnard.yaml
    - !Tar
      url: http://files.mglawica.org/barnard-dev.tar.xz
      sha256: 27fccbeeb4329c8d919f161e925cd6e63514842f6157dab23eef51f968ba7865
    END

    cat <<END > vagga/barnard.container.yaml
    auto-clean: true
    setup:
    - !*Unpack [!*Include "barnard.yaml"]
    <<END

    cat <<END > vagga/barnard.command.yaml
    !Command
    description: Run barnard (a container deployment tool)
    container: barnard
    run:
    - barnard
    <<END

Insert the following into your ``vagga.yaml`` (put in respective sections)::

    containers:
        barnard: !*Include "vagga/barnard.container.yaml"

    commands:
        barnard: !*Include "vagga/barnard.command.yaml"

Done. Yes **we are working on oneliner** like ``curl ... | sh`` to do it
for you!

Now you should annotate command you want to use with some metadata:

    commands:
      run: !Command
        container: py
        description: Run the application
        _mglawica:
          name: bar
          port: 10001
          files: [foobar, setup.py]
        run: [/usr/bin/python3, -m, foobar]

As you might guessed ``_mglawica`` key is our annotation, it conists of:

* name of the app, it's both a hostname prefix and name of your app in
  monitoring
* port number where to service will listen, you need to choose different
  port for each service and you must arrange for your service to listen on
  this port yourself for now
* files (and directories) to copy to the target container, vagga will version
  all the files in these directories to version containers so keep list
  minimal

Another issue is that you **must update your executable name** to use full
path. (We'll fix that later)

Now generate lithos configs::

    vagga barnard check -u

When you update vagga config run ``check -u`` again, it will ensure that
things are not out of sync. You may review and ``barnard/lithos.*.yaml``
and adjust memory limit or other things.

Now (hopefully) we can deploy::

    vagga barnard deploy

If thing you're deploying is not a git repository you might specify version
manually (see ``--help``), just ensure that any change is deployed with new
version.


Destroy a Node
==============

If you kept your terraform state you can use the tool to destroy machine::

    terraform destroy -var-file=key.tfvars
