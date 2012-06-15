# encoding: utf-8
import os
try:
    import urllib2
except ImportError: # Python >= 3
    import urllib.request as urllib2
import csv

from nose.tools import eq_

PYPI_MD5_URL = 'http://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'distribute-0.6.27.tar.gz': 'ecd75ea629fee6d59d26f88c39b2d291',
    'virtualenv-1.7.1.2.tar.gz': '3be8a014c27340f48b56465f9109d9fa',
    'virtualenvwrapper-3.3.tar.gz': '7e334cec98d800dcd8e4959502616d16',
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
