========
Mglawica
========

:Status: Proof of Concept

The basic idea here is to start with Dokku_-like experience to make first
deployment as easy as possible, but allow to scale a cluster to several nodes.

Theoretically you could continue to scale the cluster beyond several nodes,
but usually this uncovers more details specific to your project. Which
basically means you will fork our scripts, tweak verwalter_'s scheduler and
continue use the tools on your own.

This project is built with vagga_, cantal_, lithos_ and verwalter_. We also
use nginx, rsync, linux and more, they are pretty ubuquitous, though.

See `Verwalter's concepts`_ for description of roles of all these tools, but
you don't need to learn all that. You should get used to vagga_ basics to be
productive, though. Luckily there are `plenty of tutorials`_.

.. _dokku: https://github.com/dokku/dokku
.. _lithos: http://lithos.readthedocs.org
.. _vagga: http://vagga.readthedocs.org
.. _cantal: http://cantal.readthedocs.org
.. _verwalter: http://verwalter.readthedocs.org
.. _verwalter's concepts: http://verwalter.readthedocs.io/en/latest/info/concepts.html
.. _plenty of tutorials: http://vagga.readthedocs.io/en/latest/examples.html


License
=======

Licensed under either of

 * Apache License, Version 2.0, (./LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license (./LICENSE-MIT or http://opensource.org/licenses/MIT)

at your option.

------------
Contribution
------------

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in the work by you, as defined in the Apache-2.0
license, shall be dual licensed as above, without any additional terms or
conditions.
