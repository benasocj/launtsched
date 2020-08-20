Launtsched
==========

What is this?
-------------

I wanted a way to be able to schedule pausing and unpausing my `Launtel
<https://launtel.net.au>`__ internet service.

Launtsched (short for Launtel scheduler) is a simple Python script for now but
in future this could potentially be done through a GUI too.

How do I use this?
------------------

* Configure the ``USERNAME`` and ``PASSWORD`` fields at the top of the script
  with your Launtel login details.
* Create a Python ``venv`` (virtual environment) and install the ``requests``
  Python package inside it (I use Python's ``pip`` for the installation).
* Run the Python script with the ``pause`` or ``unpause`` argument, such as::

    python3 change_service_status.py pause

How do you schedule this?
-------------------------

I run a free Compute Engine instance on Google Cloud Platform which runs on
Linux. I use the ``at`` command to schedule the execution of the script at a
certain time.

For example, to pause my service at 23:55 I run the following::

  echo 'python3 launtel_change_service_status.py pause'|at 23:55

Or to schedule an unpause for a future date::

  echo 'python3 launtel_change_service_status.py unpause'|at 00:05 2021-01-01
