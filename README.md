# Virtualenv Burrito [![status](http://stillmaintained.com/brainsik/virtualenv-burrito.png)](http://stillmaintained.com/brainsik/virtualenv-burrito) #

With one command, have a working [virtualenv](http://pypi.python.org/pypi/virtualenv) +
[virtualenvwrapper](http://pypi.python.org/pypi/virtualenvwrapper)
environment.

## Install ##

    curl -s https://raw.github.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | bash

## Use

See the
[virtualenvwrapper quickstart](http://www.doughellmann.com/docs/virtualenvwrapper/install.html#quick-start)
or read the
[virtualenvwrapper command reference](http://www.doughellmann.com/docs/virtualenvwrapper/command_ref.html).

### Quickstart ###

To create a new virtualenv:

    mkvirtualenv newname

Once activated, `pip install <package>` (_without_ using sudo) whichever Python
packages you want. They'll only be available in that virtualenv. You can make
as many virtualenvs as you want.

To switch between virtualenvs:

    workon othername

## Upgrade ##

To upgrade to the latest virtualenv + virtualenvwrapper packages:

    virtualenv-burrito upgrade

## Why ##

To get Python coders coding.

Virtualenv Burrito was inspired by
[Pycon sprinters](http://us.pycon.org/2011/sprints/) who wasted time getting
virtualenv setup so they could start hacking on code. It's sadly
complicated to quickly setup the wonderful virtualenv + virtualenvwrapper
environment. Depending on your system you may end up yak shaving with
setuptools, distribute, virtualenv, virtulenvwrapper, .bashrc, PyPI,
apt-get/MacPorts, and more.

A second feature is the ability to upgrade to newer versions of virtualenv and
virtualenvwrapper with a single command.

## Multiple Pythons ##

With Virtualenv Burrito, it's possible to create virtualenvs using different
Python interpreters. For example, you can use `mkvirtualenv` to create a Python
2.7 virtualenv and then use it to make a Python 2.5 virtualenv. It's considered
experimental, but I have yet to hit any problems.

To try it out, see the article
[Virtualenvs with different interpreters](http://bsik.net/p8685119046).
You can also view my example of
[creating a virtualenv using PyPy](https://github.com/brainsik/virtualenv-burrito/issues/13#issuecomment-2200184).

## Credits ##

The real hard work is done by the creators of
[Virtualenv](http://www.virtualenv.org/) and
[Virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/).
Virtualenv is maintained by [Ian Bicking](ianbicking.org/). Virtualenvwrapper
is maintained by [Doug Hellman](http://www.doughellmann.com/).

## Caveat emptor ##

This simple script is meant for people who do not have virtualenv installed.
