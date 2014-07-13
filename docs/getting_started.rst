===============
Getting Started
===============

Installation
============

With PyPI
---------

.. code-block:: shell

    pip install wagtailforums


From git
--------

.. code-block:: shell

    pip install -e git://github.com/kaedroho/wagtailforums.git#egg=wagtailforums


Configuration
=============

Simply add ``wagtailforums`` into your ``INSTALLED_APPS``. Anywhere after the ``wagtail.*`` imports will do.

.. code-block:: python

    INSTALLED_APPS = [
        ...

        'wagtailforms',
    ]
