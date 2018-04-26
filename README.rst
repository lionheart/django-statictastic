django-statictastic
===================

A fantastic way to keep your static files in sync with your storage
backend of choice.

See http://dlo.me/archives/2013/01/14/how-to-serve-static-files-django/
for more background and usage.

Versioning
----------

This library supports both Python 2 and 3, but are maintained on two
separate branches and therefore you’ll need to specify which version you
want through your requirements file.

If you’re running on Python 3.0 or greater, use this:

::

    statictastic>=3.0

If you’re running on Python 2.7 or earlier, use the following instead:

::

    statictastic>=1.0,<=2.0
