#!/usr/bin/env python

import sys
import re
import requests
from hashlib import sha1
from subprocess import check_call

pypi_index_url = 'https://pypi.python.org/pypi/%s/json'
pypi_version_url = 'https://pypi.python.org/pypi/%s/%s/json'

# Order here matters since this is used for writing to files
software = ('_virtualenv-burrito', 'setuptools', 'pip', 'virtualenv', 'virtualenvwrapper')


def out(msg, err=False, nl=True):
    if err:
        fp = sys.stderr
    else:
        fp = sys.stdout
    if not isinstance(msg, basestring):
        msg = repr(msg)
    fp.write(msg)
    if nl:
        fp.write('\n')
    fp.flush()


def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def shasum(url):
    out('-> getting shasum .', nl=False)
    m = sha1()
    for b in requests.get(url, stream=True).iter_content(chunk_size=1024 * 50):
        m.update(b)
        out('.', nl=False)
    digest = unicode(m.hexdigest())
    out(' %s' % digest)
    return digest


def extract_csv():
    versions = {}

    with open('versions.csv') as fp:
        versions_csv = fp.read().strip()

    for l in versions_csv.splitlines():
        name, version, url, shasum = l.strip().split(',')
        versions[name] = {
            'version': version,
            'url': url,
            'shasum': shasum,
        }

    return versions


def commit_msg(upgrades):
    msg = []
    for name in software:
        if name in upgrades:
            msg.append('%s %s' % (name, upgrades[name]['version']))
    return ', '.join(msg)


def update_csv(upgrades):
    names = upgrades.keys()

    with open('versions.csv') as fp:
        csv = fp.readlines()

    with open('versions.csv', 'w') as fp:
        for l in csv:
            for n in names:
                if l.startswith(n+','):
                    l = ','.join([n, upgrades[n]['version'], upgrades[n]['url'], upgrades[n]['shasum']]) + '\n'
            fp.write(l)


def update_test_download(upgrades):
    names = upgrades.keys()

    with open('test_download.py') as fp:
        py = fp.readlines()

    with open('test_download.py', 'w') as fp:
        found, done = False, False
        for l in py:
            if done:
                pass
            elif not found:
                if l.startswith('PYPI_DOWNLOADS = {'):
                    found = True
            else:
                if l.strip()[0] == '#':
                    pass
                elif l.strip()[0] == '}':
                    done = True
                else:
                    tmp = l.strip()
                    for n in names:
                        if l.startswith("    '%s-" % n):
                            l = "    '%s-%s.tar.gz': '%s',\n" % (
                                n, upgrades[n]['version'], upgrades[n]['md5sum'],
                            )
            fp.write(l)


def extract_test_download():
    found = False
    files = {}
    with open('test_download.py') as fp:
        for l in fp:
            l = l.strip()
            if not found:
                if l.startswith('PYPI_DOWNLOADS = {'):
                    found = True
            else:
                if l[0] == '#':
                    continue
                if l[0] == '}':
                    return files
                name, version, md5sum = re.match(r'^\'([a-z]+)?-((?:\d\.?)+)\.tar\.gz\': \'([a-f0-9]{32})\',$', l).groups()
                files[name] = {
                    'version': version,
                    'md5sum': md5sum,
                }


def get_latest(pkg):
    return fetch_json(pypi_index_url % pkg)['info']['version']


def get_pkg(pkg, version=None):
    if version is None:
        version = get_latest(pkg)
    out('fetching %s==%s' % (pkg, version))
    for url in fetch_json(pypi_version_url % (pkg, version))['urls']:
        if url['packagetype'] == 'sdist':
            return {
                'version': version,
                'url': url['url'],
                'md5sum': url['md5_digest'],
                'shasum': shasum(url['url']),
            }


def get_current_versions():
    versions = extract_csv()
    md5sums = extract_test_download()
    for k, v in md5sums.iteritems():
        assert versions[k]['version'] == v['version']
        versions[k]['md5sum'] = v['md5sum']
    return versions



if __name__ == '__main__':
    upgrades = {}
    versions = get_current_versions()

    # First, check for updates to virtualenvwrapper
    pkg = get_pkg('virtualenvwrapper')
    if pkg != versions['virtualenvwrapper']:
        upgrades['virtualenvwrapper'] = pkg


    # virtualenv brings pip and setuptools
    pkg = get_pkg('virtualenv')
    if pkg != versions['virtualenv']:
        upgrades['virtualenv'] = pkg

        # HACK: virtualenv is missing it's 15.2.0 tag
        if pkg['version'] == '15.2.0':
            ref = '61255cf0397a7d5f73e1f070a3d32ed620c63780'
        else:
            ref = pkg['version']

        # Check the contained files from GitHub
        files = fetch_json('https://api.github.com/repos/pypa/virtualenv/contents/virtualenv_support?ref=%s' % ref)

        for name in ('pip', 'setuptools'):
            for f in files:
                if f['name'].startswith(name):
                    version = re.match(r'^[a-z]+-((?:\d\.?)+).+', f['name']).group(1)
                    pkg = get_pkg(name, version)
                    if pkg != versions[name]:
                        upgrades[name] = pkg

    if not upgrades:
        out('Everything is up to date.')
        sys.exit(0)

    out('')
    for name in software:
        if name in upgrades:
            out('%s %s -> %s' % (name, versions[name]['version'], upgrades[name]['version']))

    check_call('git reset --hard HEAD', shell=True)

    update_csv(upgrades)
    update_test_download(upgrades)

    check_call('py.test -v test_download.py', shell=True)
    check_call('git add versions.csv test_download.py', shell=True)
    check_call('git commit -m "%s"' % commit_msg(upgrades), shell=True)
    check_call('git show HEAD', shell=True)
