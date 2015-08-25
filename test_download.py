# encoding: utf-8
import os
import urllib2
import csv
import hashlib

from nose.tools import eq_

PYPI_MD5_URL = 'https://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'setuptools-18.2.tar.gz': '52b4e48939ef311d7204f8fe940764f4',
    'pip-7.1.2.tar.gz': '3823d2343d9f3aaab21cf9c917710196',
    'virtualenv-13.1.2.tar.gz': 'b989598f068d64b32dead530eb25589a',
    'virtualenvwrapper-4.6.0.tar.gz': 'b6928707eb17152b6a14fd6eeb2931a3',
}


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
