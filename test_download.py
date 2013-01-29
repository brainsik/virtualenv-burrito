# encoding: utf-8
import os
import urllib2
import csv
import hashlib

from nose.tools import eq_

PYPI_MD5_URL = 'http://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'distribute-0.6.34.tar.gz': 'b6f9cfbaf3e63833b71009812a613be13e68f5de',
    'virtualenv-1.8.4.tar.gz': '1c7e56a7f895b2e71558f96e365ee7a7',
    'virtualenvwrapper-3.6.tar.gz': '57d78305b75750a40985f206c80a280f',
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
        urllib2.urlopen(PYPI_MD5_URL + md5sum)
