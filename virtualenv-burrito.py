#!/usr/bin/env python
# encoding: utf-8
#
#   virtualenv-burrito.py — manages the Virtualenv Burrito environment
#

__version__ = "2.7"

import sys
import os
import csv
import urllib2
import shutil
import glob
import tempfile
import platform

try:
    import hashlib
    sha1 = hashlib.sha1
except ImportError:  # Python < 2.5
    import sha
    sha1 = sha.new

try:
    import subprocess
    sh = lambda cmd: subprocess.call(cmd, shell=True)
except ImportError:  # Python < 2.4
    sh = os.system

NAME = os.path.basename(__file__)
VENVBURRITO = os.path.join(os.environ['HOME'], ".venvburrito")
VENVBURRITO_LIB = os.path.join(VENVBURRITO, "lib")
VERSIONS_URL = "https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/versions.csv"


def get_python_maj_min_str():
    return ".".join(platform.python_version().split(".")[:2])


def get_python_lib_paths():
    lib_paths = []
    for pydir in glob.glob(os.path.join(VENVBURRITO_LIB, "python*")):
        if os.path.exists(os.path.join(pydir, "site-packages")):
            pydir = os.path.join(pydir, "site-packages")
        lib_paths.append(pydir)
    lib_paths.sort()
    lib_paths.reverse()
    return lib_paths


def get_installed_version(name):
    """Returns current version of `name`."""
    versions = []
    for pydir in get_python_lib_paths():
        for egg_path in glob.glob("%s-*.egg*" % os.path.join(pydir, name)):
            egg = os.path.basename(egg_path)
            versions.append(map(int, egg.split('-')[1].split('.')))
    if versions:
        return ".".join(map(str, max(versions)))


def download(url, digest):
    """Returns a filename containing the contents of the URL.

    Downloads and checks the SHA1 of the data matches the given hex digest.
    """
    name = url.split('/')[-1]
    print "  Downloading", name, "…"
    try:
        download_data = urllib2.urlopen(url).read()
    except Exception, e:
        sys.stderr.write("\nERROR - Unable to download %s: %s %s\n"
                         % (url, type(e), str(e)))
        raise SystemExit(1)

    filehash = sha1()
    filehash.update(download_data)
    if filehash.hexdigest() != digest:
        print ("\nThe file %s didn't look like we expected.\n"
               "It may have been moved or tampered with. You should tell me:"
               " @brainsik." % name)
        raise SystemExit(1)

    downloaded_file = tempfile.NamedTemporaryFile("wb", delete=False)
    downloaded_file.write(download_data)
    downloaded_file.close()
    return downloaded_file.name


def drop_startup_sh():
    # create the startup script
    script = """
export WORKON_HOME="$HOME/.virtualenvs"
export PIP_VIRTUALENV_BASE="$WORKON_HOME"
export PIP_RESPECT_VIRTUALENV=true

venvb_py_path="$HOME/.venvburrito/lib/python%s/site-packages"
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
""" % get_python_maj_min_str()
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


def _getcwd():
    try:
        return os.getcwd()
    except OSError:
        return None


def upgrade_package(filename, name, version):
    """Install Python package in tarball `filename`."""
    pyver = "python%s" % get_python_maj_min_str()
    lib_python = os.path.join(VENVBURRITO_LIB, pyver, "site-packages")

    pythonpath = ''
    for pydir in reversed(get_python_lib_paths()):
        pythonpath += "%s:" % pydir
    os.environ['PYTHONPATH'] = pythonpath.rstrip(":")

    realname = "%s-%s" % (name, version)
    print "  Installing", realname

    owd = _getcwd()
    tmp = tempfile.mkdtemp(prefix='venvburrito.')
    try:
        # unpack the tarball
        sh("tar xfz %s -C %s" % (filename, tmp))
        os.chdir(os.path.join(tmp, realname))

        if name in ['setuptools', 'distribute']:
            # build and install the egg to avoid patching the system
            sh("%s setup.py bdist_egg" % sys.executable)
            egg = glob.glob(os.path.join(os.getcwd(), "dist", "*egg"))[0]
            sh("%s setup.py easy_install --exclude-scripts --install-dir %s %s >/dev/null"
               % (sys.executable, lib_python, egg))

        elif name == 'pip':
            libexec = os.path.join(VENVBURRITO, "libexec")
            sh("%s setup.py install --prefix='' --home='%s' --install-lib %s --install-scripts %s --no-compile >/dev/null"
               % (sys.executable, VENVBURRITO, lib_python, libexec))

        else:
            pip = os.path.join(VENVBURRITO, "libexec", "pip")
            sh("%s install --install-option='--prefix=%s' ." % (pip, VENVBURRITO))
    finally:
        os.chdir(owd or VENVBURRITO)
        shutil.rmtree(tmp)


def check_versions(selfcheck=True):
    """Return packages which can be upgraded."""
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
        if not os.path.exists(os.path.join(VENVBURRITO, "libexec")):
            print "! Removing burrito < 2.7 setup and preparing fresh wrap"

            # nuke old lib and get pip out of the bin PATH
            shutil.rmtree(VENVBURRITO_LIB)
            for pip in glob.glob(os.path.join(VENVBURRITO, "bin", "pip*")):
                os.remove(pip)

            # create versioned python site-packages dir
            pyver = "python%s" % get_python_maj_min_str()
            os.mkdir(VENVBURRITO_LIB)
            os.mkdir(os.path.join(VENVBURRITO_LIB, pyver))
            os.mkdir(os.path.join(VENVBURRITO_LIB, pyver, "site-packages"))

    has_update = check_versions(selfupdated is False)

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

    if argv[1] in ['version', '--version', '-V']:
        print "virtualenv-burrito %s from %s" % (__version__, __file__)
        raise SystemExit(0)

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
