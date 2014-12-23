# encoding: utf-8
import os
import urllib2
import csv
import hashlib

from nose.tools import eq_

PYPI_MD5_URL = 'https://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'setuptools-8.2.tar.gz': '631c3b2d0e6868d77fcf11d9de8fe7a7',
    'pip-1.4.1.tar.gz': '6afbb46aeb48abac658d4df742bff714',
    'virtualenv-12.0.2.tar.gz': 'cd43c130badf76ecb3c6bf72a14c42f6',
    'virtualenvwrapper-4.3.1.tar.gz': '4327d04b0e65d4229352454ab8ce3f37',
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
