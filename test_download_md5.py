# encoding: utf-8
import os
import urllib2
import csv

from nose.tools import eq_

PYPI_MD5_URL = 'http://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'distribute-0.6.21.tar.gz': 'f783444754861f9b33e9f4083bd97b60',
    'virtualenv-1.6.4.tar.gz': '1072b66d53c24e019a8f1304ac9d9fc5',
    'virtualenvwrapper-2.8.tar.gz': '4998181c67fad05a6429e1ca84d638b1',
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


def test_md5_exists():
    for ball, md5sum in PYPI_DOWNLOADS.iteritems():
        urllib2.urlopen(PYPI_MD5_URL + md5sum)
