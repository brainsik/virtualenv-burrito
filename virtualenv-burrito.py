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


def selfupdate(src):
    """Copy src to our destination and exec the new script."""
    dst = os.path.join(VENVBURRITO, "bin", "virtualenv-burrito")
    shutil.copyfile(src, dst)
    os.remove(src)
    os.chmod(dst, 0755)
    print "  Restarting!\n"
    sys.stdout.flush()
    # pass "no-selfcheck" so we don't accidentally loop infinitely
    os.execl(dst, "virtualenv-burrito", "upgrade", "no-selfcheck")


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
        if name == 'virtualenv':
            # keep virtualenv from using a specific Python interpreter
            print "  Fixing bin/virtualenv"
            cmd = ("perl -pe 's|^#!.*|#!/usr/bin/env python|' %s"
                   % os.path.join(VENVBURRITO, "bin", "virtualenv"))
            print cmd
            print sh(cmd)
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


def handle_upgrade(selfcheck=True):
    """Handles the upgrade command."""
    if os.path.exists(VENVBURRITO_LIB):
        if not os.path.isdir(os.path.join(VENVBURRITO_LIB, "python")):
            print "! Removing old v1 packages and doing fresh v2 install"
            shutil.rmtree(VENVBURRITO_LIB)
            os.mkdir(VENVBURRITO_LIB)
            os.mkdir(os.path.join(VENVBURRITO_LIB, "python"))

    has_update = check_versions(selfcheck)
    if not has_update:
        print "Everything is up to date."
        raise SystemExit(0)

    # update ourself first
    for update in has_update:
        if update[0] == NAME:
            print "* Upgrading ourself …"
            filename = None
            url, digest = has_update[2:]
            try:
                filename = download(url, digest)
                selfupdate(filename)  # calls os.exec
            finally:
                if filename and os.path.exists(filename):
                    os.remove(filename)

    for update in has_update:
        filename = None
        name, version, url, digest = update
        print "* Upgrading %s …" % name
        try:
            filename = download(url, digest)
            upgrade_package(filename, name, version)
        finally:
            if filename and os.path.exists(filename):
                os.remove(filename)

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
        if len(argv) > 2 and argv[2] == 'no-selfcheck':
            handle_upgrade(selfcheck=False)
        else:
            handle_upgrade()
    else:
        usage()


if __name__ == '__main__':
    main(sys.argv)
