# encoding: utf-8
import os
import urllib2
import csv

from nose.tools import eq_

PYPI_MD5_URL = 'http://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'distribute-0.6.27.tar.gz': 'ecd75ea629fee6d59d26f88c39b2d291',
    'virtualenv-1.7.2.tar.gz': 'b5d63b05373a4344ae099a68875aae78',
    'virtualenvwrapper-3.5.tar.gz': '69f51d186845b584c0ef09e258818fe7',
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
