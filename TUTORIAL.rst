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

    curl -sSf http://mglawica.org/barnard-bootstrap.sh | sh

