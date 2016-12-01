Tutorial
========

In this tutorial we will create a "Hello world" web application in python and
deploy it in mglawica cluster.

Prerequisites:

* You can read some python code and have built some tutorial services
* You are familiar with using terminal and command-line
* You can install needed OS packages
* You have basic internet knowledge, know what TCP ports are and how
  to navigate to the web service with non-default port
* Basic knowledge of git is expected too
* You have an account and ten cents for experiments in `Digital Ocean`_

Start with:

* Install vagga_, terraform_ and tinc_ (``apt-get install tinc``)
* ``git clone https://github.com/tailhook/mglawica ~/mgl-common``
* ``mkdir ~/mgl-hello; cd ~/mgl-hello``

.. _vagga: https://vagga.readthedocs.io/en/latest/installation.html
.. _tinc: https://vagga.readthedocs.io/en/latest/installation.html
.. _terraform: https://www.terraform.io/downloads.html
.. _Digital Ocean: https://digitalocean.com


Bootstrap Application
=====================

Create ``hello.py``:

.. code-block:: python

    import asyncio
    from aiohttp import web

    async def hello(request):
        return web.Response(body=b"Hello, world", content_type="text/plain")

    app = web.Application()
    app.router.add_route('GET', '/', hello)
    web.run_app(app, port=10000)

As you can see we used super-puper brilliant new technology called ``asyncio``.
You don't have to know all the details to get it running. Just try it and
replace with your favourite thing when ready.

To run it without headache add the following ``vagga.yaml``:

.. code-block:: yaml

    containers:
      py:
        setup:
        - !Alpine v3.4
        - !PipConfig { dependencies: true }
        - !Py3Install [aiohttp]

    commands:
      run: !Command
        container: py
        description: Run the application
        run: "python3 hello.py"

That's all needed to run it, try:

.. code-block:: console

    $ vagga run
     ... some container build messages ...
    ======== Running on http://0.0.0.0:10000 ========
    (Press CTRL+C to quit)

Okay, you can go to the http://localhost:10000 to see if your app works
locally.

It's good idea to ``git commit`` at this point. Don't forget to add ``.vagga``
directory to your ``.gitignore``.


Bootstrapping Barnard
=====================

``barnard`` is an utility that deploys your application to the cluster.
We'll setup cluster shortly in the meantime we can prepare all the configs.

First, bootstrap the barnard::

    curl -sSf http://sh.mglawica.org/barnard-testing.sh | sh

(We only have ``-testing`` version so far)

First it puts bootstrap code into your vagga.yaml then asks few questions
and adds some metadata to vagga.yaml. Here is the example session::

    vagga is /usr/bin/vagga
    mktemp is /usr/bin/mktemp
    vagga.yaml 226 8 81a4 1000 100 fe03 128529 1 0 0 1480538587 1480538587 1480538587 0 4096
    Ready. Copying files...

    ------------------------------------------------------------------
    Running `vagga barnard bootstrap`... You may do this at any time

    Okay. We are going to add some small but important metadata
    to your vagga.yaml file.

    Don't be too cautious here, you can edit it later
    directly in vagga.yaml

    Available commands: run
    Which command you want to deploy: run
    Got it. Command: 'run'

    You need some name for the program that is global to your cluster
    Role name: hello-world
    'run' is good name. Just few things left.

    You need a free port on your host system. Different services must
    allocate different ports. Good value is somewhere
    in the range 10000-20000
    Port: 10000

    The last step is to choose which files are going to be deployed.
    Container is always deployed, but probably you will need some
    files from your working directory

    Your directory list: vagga vagga.yaml hello.py

    Enter space separated list of files and directories. Vagga will
    version them properly as part of container. You can edit the list
    later
    Files: hello.py
    Fine. Your config is:

    commands:
      run: !Command
        # .. command config ...
        _mglawica:
          files: [hello.py]
          port: 10000
          role: hello-world

    We'll try to put it in file, but this sometimes fails

    Fine. You may want to commit now:
      git add vagga/ vagga.yaml
      git commit
    Then run:
      vagga barnard check -u
      vagga barnard deploy

It's now good idea to commit the file as described. Then run::

    vagga barnard check -u

This generates the following files:

* ``barnard/lithos.yaml`` -- a configuration that describes the command
  that will be run in production environment. You might want to edit its
  command line and/or limits on resources.
* ``vagga/_deploy-py.container.yaml`` -- a file that describes how to build
  a filesystem image for the container

Despite these files are initially generated we commit them to version control
anyway. Every time you change vagga.yaml it's good idea to run
``vagga barnard check -u`` again.

Now we are ready to deploy, but since we haven't setup a hosting yet, we
can (and should) run a dry run deploy to ensure that everything is fine:

.. code-block:: console

    $ vagga barnard deploy --dry-run
    OK: 72 MiB in 27 packages
        => git describe --match 'v[0-9]*' --dirty
        => git rev-list HEAD
    Application name: hello-world
    Version: v0.0.0-0-gdd5c1c2
    Deployment config: {'main': {'config': '/config/lithos.main.yaml',
                                 'http-host': 'hello-world',
                                 'image': '_deploy-py.b690083b',
                                 'port': 10000}}
    All checks complete. Version v0.0.0-0-gdd5c1c2 is ready to go


Setting up Digital Ocean
========================

*Tested with terraform == 0.6.15*

First set up your digitalocean keys, and possibly a domain name:

.. code-block:: shell

    cd ~/mgl-common/terraform/digitalocean
    # create token in https://cloud.digitalocean.com/settings/api/tokens
    echo 'do_token = "xxxyour_tokenxx"' > key.tfvars
    # upload ssh key in https://cloud.digitalocean.com/settings/security
    echo 'do_ssh_key = "12:34:56:78:9a:bc:de:f1"' >> key.tfvars
    # **optional** public host (wildcard host should be configured)
    echo 'public_host = "my.host.whatever"' >> key.tfvars

Then just run our startup script::

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
    Next time you want to connect to VPN again run:
      ./tink/start.sh
    from current directory

That's it for configuring VM.

.. note:: Terraform writes state files directly into this directory, and
   we write `tinc` keys here too. So you should keep this directory around.

Now you can deploy your first project:


.. code-block:: console

    $ cd ~/mgl-hello
    $ vagga barnard deploy
        => git describe --match 'v[0-9]*' --dirty
        => git rev-list HEAD
    Application name: hello-world
    Version: v0.0.0-0-gdd5c1c2
    Deployment config: {'main': {'config': '/config/lithos.main.yaml',
                                 'http-host': 'hello-world',
                                 'image': '_deploy-py.b690083b',
                                 'port': 10000}}
        => rsync -rlp /target/_deploy-py/ rsync://172.24.0.1/images/hello-world/_deploy-py.tmp
        .. done in 12 sec
    Done v0.0.0-0-gdd5c1c2 App should be restarted shortly...
    Service main is accessible at:
    http://h1.mglawica.org:10000/ (VPN only)
    http://hello-world.46.101.221.105.xip.io/
    http://hello-world.h1.mglawica.org/

If you configured public host name it will be displayed here too. But if not
we also have an ugly but always working name that ends with ``xip.io``, which
is publicly accessible and ``h1.mglawica.org`` which is only accessible from
inside the VPN.


Workflow
========

Usually when you change just sources of your project run::

    vagga barnard deploy

You should create a `git tag`_ for each of your deploy, so workflow should
be rather this::

    git commit
    git tag -a v1.2.3
    git push origin master v1.2.3
    vagga barnard deploy

If you change ``vagga.yaml`` you should re-check your files::

    vagga barnard check -u
    git commit vagga.yaml barnard vagga -m "Updated containers"
    git tag -a v1.2.3
    git push origin master v1.2.3
    vagga barnard deploy

.. _git tag: https://git-scm.com/book/en/v2/Git-Basics-Tagging


Troubleshooting
===============

Here (VPN link) you can see the ports that applications occupy, in case
you made a mistake:

http://h1.mglawica.org:22682/local/users

Here you can find logs of your application:

http://h1.mglawica.org:8379/logs?filter=hello-world

The interface is *super ugly* we are working on that. What you should know,
that there are three logs for your service:

* Log of verwalter generating configs for your service (container errors)
* Log of container startup ``lithos/hello-world.log``
* Log of container's own stdio ``lithos/stderr/hello-world.log``

Here is a nice page with the list of your services:

http://h1.mglawica.org:8379/services

You can see which version is running and switch version here:

http://h1.mglawica.org:8379/role/hello-world


Maintenance
===========

**Connect to VPN** again, for example after system reboot::

    cd ~/mgl-common
    ./tinc/start.sh

**SSH access**::

    ssh root@h1.mglawica.org

(you can probably also use public IP, you can look for it in
``terraform.tfstate``)

**Stopping a cluster**::

    cd ~/mgl-common/terraform/digitalocean
    terraform destroy -var-file=key.tfvars
