# encoding: utf-8
import os
import urllib2
import csv
import hashlib
import json


PYPI_JSON_URL = 'https://pypi.org/pypi/%s/json'

PYPI_DOWNLOADS = {
    # filename: md5sum
    'setuptools-39.1.0.zip': 'cf5bb20db69412b71163c7d84ca42847',
    'pip-10.0.1.tar.gz': '83a177756e2c801d0b3a6f7b0d4f3f7e',
    'virtualenv-16.0.0.tar.gz': '4feb74ee26255dd7e62e36ce96bcc4c6',
    'virtualenvwrapper-4.8.2.tar.gz': '8e3af0e0d42733f15c5e36df484a952e',
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
        if ball.endswith('.zip'):
            filename = ball[:-4]
        else:
            # .tar.gz
            filename = ball[:-7]
        package, release = filename.split('-', 1)
        try:
            data = json.load(urllib2.urlopen(PYPI_JSON_URL % package))
        except urllib2.HTTPError as e:
            assert False, "Failed to open %s: %s %s" % (url, type(e), e)

        found = False
        release = data['releases'][release]
        for file in release:
            if file['filename'] == ball:
                assert file['md5_digest'] == md5sum
                found = True
                break

        if not found:
            assert False, 'Missing file %s %s' % (ball, md5sum)
