# encoding: utf-8
import os
import urllib2
import csv

from nose.tools import eq_

PYPI_MD5_URL = 'http://pypi.python.org/pypi?:action=show_md5&digest='

PYPI_DOWNLOADS = {
    # filename: md5sum
    'distribute-0.6.24.tar.gz': '17722b22141aba8235787f79800cc452',
    'virtualenv-1.6.4.tar.gz': '1072b66d53c24e019a8f1304ac9d9fc5',
    'virtualenvwrapper-2.11.1.tar.gz': 'dc65934feece5fd51fd0454114329392',
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
