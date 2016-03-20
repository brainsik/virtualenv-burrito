# encoding: utf-8
import os
import urllib2
import csv
import hashlib


PYPI_MD5_URL = 'https://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'setuptools-20.3.tar.gz': '1b6ec3c0cc7e15ed67fe8f0fd1d899d0',
    'pip-8.1.1.tar.gz': '6b86f11841e89c8241d689956ba99ed7',
    'virtualenv-15.0.1.tar.gz': '28d76a0d9cbd5dc42046dd14e76a6ecc',
    'virtualenvwrapper-4.7.1.tar.gz': '3789e0998818d9a8a4ec01cfe2a339b2',
}


def eq_(a, b, msg=None):
    if not a == b:
        raise AssertionError(msg or "%r != %r" % (a, b))


def test_tarball_names():
    tarballs = set()
    with open('versions.csv', 'r') as fo:
        reader = csv.reader(fo)
        for name, version, url, digest in reader:
            if name.startswith('_'):
                continue
            tarballs.add(os.path.basename(url))

    eq_(tarballs, set(PYPI_DOWNLOADS.keys()))


def test_shasum():
    with open('versions.csv', 'r') as fo:
        reader = csv.reader(fo)
        for name, version, url, digest in reader:
            if name.startswith('_'):
                continue
            sha1 = hashlib.sha1()
            sha1.update(urllib2.urlopen(url).read())
            eq_(digest, sha1.hexdigest())


def test_md5_url_exists():
    for ball, md5sum in PYPI_DOWNLOADS.iteritems():
        url = PYPI_MD5_URL + md5sum
        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            assert False, "Failed to open %s: %s %s" % (url, type(e), e)
