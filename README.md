# Virtualenv Burrito

With one command, have a working [virtualenv](http://www.virtualenv.org/) +
[virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/)
environment.

## Install

    curl -s https://github.com/brainsik/virtualenv-burrito/raw/master/virtualenv-burrito.sh | bash

## Usage

To create a new virtualenv:

    mkvirtualenv newname

To use a previously created virtualenv:

    workon somename

Once the virtualenv is activated, you can pip install (without using sudo)
whatever Python packages you want and they'll only be available in that
virtualenv.

Those commands are from Doug Hellman's excellent virtualenwrapper. To learn
more, see his [virtualenvwrapper
quickstart](http://www.doughellmann.com/docs/virtualenvwrapper/install.html#quick-start)
or read the [virtualenvwrapper command
reference](http://www.doughellmann.com/docs/virtualenvwrapper/command_ref.html).

## Why

To get Python coders coding.

Virtualenv Burrito was inspired by Pycon sprinters who wasted time getting
virtualenv setup so they could start hacking on code. It's depressingly
complicated to quickly setup the wonderful virtualenv + virtualenvwrapper
environment. Depending on your system you may end up dicking around with
setuptools, distribute, virtualenv, virtulenvwrapper, .bashrc, PyPI,
apt-get/MacPorts, and more.

## Caveat emptor

This simple script is meant for people who do not have virtualenv installed.
