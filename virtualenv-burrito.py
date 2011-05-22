#!/usr/bin/env python
# encoding: utf-8
#
#   virtualenv-burrito.py — manages the Virtualenv Burrito environment
#

__version__ = "2.0"

import sys
import os
import re
import csv
import urllib
import urllib2
import shutil
import glob
import tempfile

try:
    import hashlib  # Python 2.5
    sha1 = hashlib.sha1
except ImportError:
    import sha
    sha1 = sha.new

try:
    import subprocess  # Python 2.4
    sh = lambda cmd: subprocess.call(cmd, shell=True)
except ImportError:
    sh = os.system

NAME = os.path.basename(__file__)
VENVBURRITO = os.path.join(os.environ['HOME'], ".venvburrito")
VENVBURRITO_LIB = os.path.join(VENVBURRITO, "lib")
VERSIONS_URL = "https://github.com/brainsik/virtualenv-burrito/raw/experimental/versions.csv"

symlink_search = re.compile('^.+/lib/([^/]+)').search


def get_installed_version(name):
    """Returns current version of `name`."""
    pkg = os.path.join(VENVBURRITO_LIB, "python", name)
    for egg in glob.glob("%s-*.egg" % pkg):
        return egg.split('-')[1]


def download(url, digest):
    """Returns a filename containing the contents of the URL.

    Downloads and checks the SHA1 of the data matches the given hex digest.
    """
    name = url.split('/')[-1]
    print "  Downloading", name, "…"
    try:
        filename = urllib.urlretrieve(url)[0]
    except Exception, e:
        sys.stderr.write("\nERROR - Unable to download %s: %s %s\n"
                         % (url, type(e), str(e)))
        raise SystemExit(1)
    filehash = sha1()

    f = open(filename, 'rb')
    filehash.update(f.read())
    f.close()

    if filehash.hexdigest() == digest:
        return filename

    print "\nThe file %s didn't look like we expeceted. It may have been moved"
    print " or tampered with. You should let me know — @brainsik."
    os.remove(filename)
    raise SystemExit(1)


def drop_startup_sh():
    # create the startup script
    script = """
export WORKON_HOME="$HOME/.virtualenvs"
export VIRTUALENV_USE_DISTRIBUTE=true
export PIP_VIRTUALENV_BASE="$WORKON_HOME"
export PIP_RESPECT_VIRTUALENV=true

venvb_py_path="$HOME/.venvburrito/lib/python"
if [ -z "$PYTHONPATH" ]; then
    export PYTHONPATH="$venvb_py_path"
elif ! echo $PYTHONPATH | grep -q "$venvb_py_path"; then
    export PYTHONPATH="$venvb_py_path:$PYTHONPATH"
fi

venvb_bin_path="$HOME/.venvburrito/bin"
if ! echo $PATH | grep -q "$venvb_bin_path"; then
    export PATH="$venvb_bin_path:$PATH"
fi

. $HOME/.venvburrito/bin/virtualenvwrapper.sh
if ! [ -e $HOME/.venvburrito/.firstrun ]; then
    echo
    echo "To create a virtualenv, run:"
    echo "mkvirtualenv <cool-name>"
    touch $HOME/.venvburrito/.firstrun
fi
"""
    startup_sh = open(os.path.join(VENVBURRITO, "startup.sh"), 'w')
    startup_sh.write(script)
    startup_sh.close()


def selfupdate(src):
    """Copy src to our destination and exec the new script."""
    dst = os.path.join(VENVBURRITO, "bin", "virtualenv-burrito")
    shutil.copyfile(src, dst)
    os.remove(src)
    os.chmod(dst, 0755)

    print "  Restarting!\n"
    sys.stdout.flush()
    os.execl(dst, "virtualenv-burrito", "upgrade", "selfupdated")


def fix_bin_virtualenv():
    """Untie the virtualenv script from a specific version of Python"""
    bin_virtualenv = os.path.join(VENVBURRITO, "bin", "virtualenv")

    fi = open(bin_virtualenv, 'r')
    fi.readline()  # skip the hash bang

    fo = open(bin_virtualenv, 'w')
    fo.write("#!/usr/bin/env python\n")
    fo.write(fi.read())

    fi.close()
    fo.close()


def upgrade_package(filename, name, version):
    """Unpacks and symlinks."""
    try:
        owd = os.getcwd()
    except OSError:
        owd = None

    realname = "%s-%s" % (name, version)
    print "  Installing", realname

    os.environ['PYTHONPATH'] = os.path.join(VENVBURRITO_LIB, "python")
    tmp = tempfile.mkdtemp(prefix='venvburrito.')
    try:
        os.chdir(tmp)
        sh("tar xfz %s" % filename)
        os.chdir(os.path.join(tmp, realname))
        sh("%s setup.py install --home %s --no-compile >/dev/null"
           % (sys.executable, VENVBURRITO))
        if name in ['virtualenv', 'virtualenvwrapper']:
            fix_bin_virtualenv()
    finally:
        os.chdir(owd or VENVBURRITO)
        shutil.rmtree(tmp)


def check_versions(selfcheck=True):
    """Return dict of packages which can be upgraded."""
    try:
        fp = urllib2.urlopen(VERSIONS_URL)
    except Exception, e:
        sys.stderr.write("\nERROR - Couldn't open versions file at %s: %s %s\n"
                         % (VERSIONS_URL, type(e), str(e)))
        raise SystemExit(1)
    reader = csv.reader(fp)

    has_update = []
    for name, version, url, digest in reader:
        if name == '_virtualenv-burrito':
            if not selfcheck:
                continue
            name = NAME
            current = __version__
        else:
            current = get_installed_version(name)

        if not current or version != current:
            print "+ %s will upgrade (%s -> %s)" % (name, current, version)
            has_update.append((name, version, url, digest))
            if name == NAME:
                break

    return has_update


def handle_upgrade(selfupdated=False, firstrun=False):
    """Handles the upgrade command."""
    if os.path.exists(VENVBURRITO_LIB):
        if not os.path.isdir(os.path.join(VENVBURRITO_LIB, "python")):
            print "! Removing old v1 packages and doing fresh v2 install"
            shutil.rmtree(VENVBURRITO_LIB)
            os.mkdir(VENVBURRITO_LIB)
            os.mkdir(os.path.join(VENVBURRITO_LIB, "python"))

    has_update = check_versions(selfupdated == False)

    # update other packages
    for update in has_update:
        name, version, url, digest = update

        filename = download(url, digest)
        try:
            if name == NAME:
                print "* Upgrading ourself …"
                selfupdate(filename)  # calls os.exec
            else:
                print "* Upgrading %s …" % name
                upgrade_package(filename, name, version)
        finally:
            if filename and os.path.exists(filename):
                os.remove(filename)

    # startup.sh needs to be created after selfupdate AND on install
    if selfupdated or firstrun:
        drop_startup_sh()

    if selfupdated:
        print "\nTo finish the upgrade, run this:"
        print "source %s/startup.sh" % VENVBURRITO

    elif not has_update:
        print "Everything is up to date."
        return

    else:
        print "\nFin."


def usage(returncode=1):
    print "Use like this:\n\t%s upgrade" % NAME
    raise SystemExit(returncode)


def main(argv):
    if len(argv) < 2:
        usage()

    if argv[1] in ['help', '--help', '-h', '-?']:
        usage(returncode=0)

    if argv[1] in ['upgrade', 'update']:
        if len(argv) > 2:
            if argv[2] in ['selfupdated', 'no-selfcheck']:
                handle_upgrade(selfupdated=True)
            elif argv[2] == 'firstrun':
                handle_upgrade(firstrun=True)
            else:
                usage()
        else:
            handle_upgrade()
    else:
        usage()


if __name__ == '__main__':
    main(sys.argv)
