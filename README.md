==============
Wagtail Forums
==============

This repo contains a simple forum system built on Wagtail CMS.

It allows a forum to be built and structured through the Wagtail admin interface. All users posts are Wagtail pages so benefit from all the features Wagtail offers to pages such as moderation workflow and revisions.


Installation
============

This can be installed through pip:

    pip install wagtailforums


You can then add it to the ``INSTALLED_APPS`` setting in your Django settings:


    INSTALLED_APPS = [
        ...

        # Put this after the wagtail imports
        'wagtailforums',
    ]


Warning
=======

This project is in very early development and doesn't include many of the features that are essential for forums (patches welcome).

It is also likely to change in backwards-incompatibile ways so be aware of that if you would like to use this in a project.
