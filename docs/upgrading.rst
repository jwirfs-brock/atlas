=========
Upgrading
=========

0.9.* to 0.10.0
===============

With version 0.10.0, the new Tastypie Authorization API is used, requiring
an upgrade to at least version 0.9.15 of Tastypie.  You'll need to 
upgrade Tastypie.  Assuming you're using pip, this looks like::

    pip install --upgrade django-tastypie

0.7 to 0.8
==========

With version 0.8, we started compressing and versioning our JavaScript and
CSS assets using Django Compressor.  You'll need to install this Django app
in your environment::

    pip install django-compressor

It also has some `dependencies <http://django_compressor.readthedocs.org/en/latest/quickstart/#dependencies>`_ which vary depending on how you
configure the app.  Namely, I needed to install BeautifulSoup to use the
``compressor.parser.LxmlParser`` parser::

    pip install "BeautifulSoup<4.0"

If you don't want to use Django Compressor, removing ``compress`` from the
``{% load %}`` statement and the ``{% compress %}`` block tags from these
templates will allow you to continue without Django Compressor: 

* storybase_story/explore_stories.html
* storybase_story/story_builder.html
* storybase_story/story_detail.html
* storybase_story/story_viewer.html
* base.html

You'll also need to remove ``compressor`` from the ``INSTALLED_APPS`` 
setting in your Django settings module.

0.5 to 0.6
==========

With version 0.6, a new Teaser model has been added to the Django CMS
integration.  In order to create the model schema in the database, run::

    manage.py migrate cmsplugin_storybase

0.4 to 0.5
==========

With version 0.5, the primary version of Django that we are supporting will
be Django 1.4.* and the primary version of Django CMS will be 2.3.*.

While we will try to maintain comaptibility with Django 1.3.1 and Django
CMS 2.2, we recommend that you should upgrade your versions of Django and
Django CMS.  

Version 0.5 also updates the dependency of django-notification to version
1.0 and this package should also be upgraded.

To ugprade the dependencies, use the following commands::

    pip install Django==1.4.3
    pip install django-mptt==0.5.2
    pip install django-reversion==1.6
    pip install django-sekizai==0.6.1
    pip install django-cms==2.3.5
    manage.py migrate cms
    pip install django-notification==1.0
