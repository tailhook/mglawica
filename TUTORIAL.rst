Tutorial
========

In this tutorial we will create a "Hello world" web application in python and
deploy it in verwalter cluster.

Prerequisites:

* You can read some python code and have built some tutorial services
* You are familiar with using terminal and command-line
* You can install needed OS packages
* You have basic internet knowledge, know what TCP ports are and how
  to navigate to the web service with non-default port
* Basic knowledge of git is expected too

Start with:

* Install vagga_, terraform_ and tinc_ (``apt-get install tinc``)
* ``git clone https://github.com/tailhook/mglawica ~/mgl-common``
* ``mkdir ~/mgl-hello; cd ~/mgl-hello``

.. _vagga: https://vagga.readthedocs.io/en/latest/installation.html
.. _tinc: https://vagga.readthedocs.io/en/latest/installation.html

Bootstart Application
=====================

Create ``hello.py``:

.. code-block:: python

    import asyncio
    from aiohttp import web

    async def hello(request):
        return web.Response(body=b"Hello, world")

    app = web.Application()
    app.router.add_route('GET', '/', hello)
    web.run_app(app)

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

    > vagga run
     ... some container build messages ...
    ======== Running on http://0.0.0.0:8080 ========
    (Press CTRL+C to quit)

Okay, you can go to the url to see if your app works locally.

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
  that will be run in production environment. You might want to edit it's
  command line and/or limits on resources.
* ``vagga/_deploy-py.container.yaml`` -- a file that describes how to build
  a filesystem image to create a container

Despite these files are initially generated we commit them to version control
anyway. Every time you change vagga.yaml it's good idea to run
``vagga barnard check -u`` again.

Now we are ready to deploy, but since we haven't setup a hosting yet, we
can (and should) run a dry run deploy to ensure that everything is fine::

    vagga barnard deploy --dry-run


