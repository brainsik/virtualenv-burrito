# encoding: utf-8
import os
import urllib2
import csv
import hashlib

from nose.tools import eq_

PYPI_MD5_URL = 'http://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'distribute-0.6.49.tar.gz': '89e68df89faf1966bcbd99a0033fbf8e',
    'pip-1.5.6.tar.gz': '01026f87978932060cc86c1dc527903e',
    'virtualenv-1.11.6.tar.gz': 'f61cdd983d2c4e6aeabb70b1060d6f49',
    'virtualenvwrapper-4.1.1.tar.gz': 'f18f2c612b936583a8ec0f7114b6637e',
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
