.. _customize_label:

========================
Customization
========================

How to add additional links to sidebar?
---------------------------------------------
In your models (for example, db.py), set :

#. plugins.instant_admin.extra_sidebar_title to the title of your sidebar.

#. plugins.instant_admin.extra_sidebar to a list of A objects.

For example, if you put this in db.py ::

    plugins.instant_admin.extra_sidebar_title = "My Custom Sidebar"
    plugins.instant_admin.extra_sidebar = [
        A('Google', _href='http://google.com'),
        A('New User', _href=URL('new', args='users')),
    ]

you will get :

.. figure:: screenshots/custom-sidebar.png


