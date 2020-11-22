Launtsched
==========

Warning
-------

As of 2020-11-22 Launtsched does not work anymore at the moment since Launtel's
API has changed. I didn't have time yet to make the necessary changes but I'm
happy for others to submit a pull request.

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

For example, to pause my service at 9 pm I run the following::

  echo 'python3 launtel_change_service_status.py pause'|at 9pm

Or to schedule an unpause for a future date::

  echo 'python3 launtel_change_service_status.py unpause'|at 0:05am 2021-01-01

Be kind and considerate to Launtel
----------------------------------

Knowing that NBN's turn around times can be fairly slow when pausing/unpausing a
service, Launtel would still have to pay for an extra day if you pause your
service at 11:59 pm but it only gets paused on NBN's side after midnight. Hence,
if you know you'll be in bed by 9 pm then `love your neighbour as yourself
<https://www.esv.org/mark12:31/>`__ and be kind to Launtel by scheduling the
pausing of your service for that time in order to give Launtel a chance to still
finish the pausing process within the same day so they don't have to pay the
extra.
