#!/bin/bash
#
# virtualenv-burrito
#
#   One command to have a working virtualenv + virtualenvwrapper environment.
#
set -e

DISTRIBUTE_URL="http://pypi.python.org/packages/source/d/distribute/distribute-0.6.15.tar.gz"
VIRTUALENV_URL="http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.5.2.tar.gz"
VIRTUALENVWRAPPER_URL="http://pypi.python.org/packages/source/v/virtualenvwrapper/virtualenvwrapper-2.6.3.tar.gz"

VENVBURRITO="$HOME/.venvburrito"
VENVBURRITO_esc="\$HOME/.venvburrito"

kernel=$(uname -s)
case "$kernel" in
    Darwin|Linux) ;;
    *) echo "Sadly, we don't support $kernel. :'("; exit 1
esac

if [ -s "$HOME/.bash_profile" ]; then
    if grep -q "$VENVBURRITO_esc/startup.sh" $HOME/.bash_profile; then
        echo "Looks like virtualenv-burrito is already installed. Bye."
        exit 1
    fi
fi


test -d $VENVBURRITO || mkdir -p $VENVBURRITO/{bin,lib}
test -d $HOME/.virtualenvs || mkdir $HOME/.virtualenvs

if [ "$kernel" == "Linux" ]; then
    tmpdir=$(mktemp -d -t venvburrito.XXXXXXXXXX)
else
    tmpdir=$(mktemp -d -t venvburrito)
fi

curl="curl"
echo -e "\nDownloading distribute …"
$curl $DISTRIBUTE_URL > $tmpdir/distribute.tar.gz
echo -e "\nDownloading virtualenv …"
$curl $VIRTUALENV_URL > $tmpdir/virtualenv.tar.gz
echo -e "\nDownloading virtualenvwrapper …"
$curl $VIRTUALENVWRAPPER_URL > $tmpdir/virtualenvwrapper.tar.gz

pushd $VENVBURRITO/lib >/dev/null

tar xfz $tmpdir/distribute.tar.gz
distribute=$(ls -dt1 $VENVBURRITO/lib/distribute-* | head -n1)
ln -snf $(basename $distribute)/pkg_resources.py .

tar xfz $tmpdir/virtualenv.tar.gz
virtualenv=$(ls -dt1 $VENVBURRITO/lib/virtualenv-* | head -n1)
ln -snf $(basename $virtualenv) $VENVBURRITO/lib/virtualenv

tar xfz $tmpdir/virtualenvwrapper.tar.gz
virtualenvwrapper=$(ls -dt1 $VENVBURRITO/lib/virtualenvwrapper-* | head -n1)
ln -snf $(basename $virtualenvwrapper)/virtualenvwrapper.sh .
ln -snf $(basename $virtualenvwrapper)/virtualenvwrapper $VENVBURRITO/lib/virtualenvwrapper

popd >/dev/null
rm -rf $tmpdir

# create the virtualenv "binary"
cat >$VENVBURRITO/bin/virtualenv <<EOF
#!/bin/bash
lib=\$(dirname \$0)/../lib
python \$lib/virtualenv/virtualenv.py \$*
EOF
chmod +x $VENVBURRITO/bin/virtualenv

# create the startup script
cat >$VENVBURRITO/startup.sh <<EOF
export WORKON_HOME="\$HOME/.virtualenvs"
export VIRTUALENV_USE_DISTRIBUTE=true
export PIP_VIRTUALENV_BASE="$WORKON_HOME"
export PIP_RESPECT_VIRTUALENV=true
if ! echo \$PYTHONPATH | grep -q "$VENVBURRITO_esc/lib"; then
    export PYTHONPATH="$VENVBURRITO_esc/lib:\$PYTHONPATH"
fi
if ! echo \$PATH | grep -q "$VENVBURRITO_esc/bin"; then
    export PATH="$VENVBURRITO_esc/bin:\$PATH"
fi
. $VENVBURRITO_esc/lib/virtualenvwrapper.sh
if ! [ -e $VENVBURRITO_esc/.firstrun ]; then
    echo
    echo "To create a virtualenv, run:"
    echo "mkvirtualenv <cool-name>"
    touch $VENVBURRITO_esc/.firstrun
fi
EOF

# startup virtualenv-burrito in the bash_profile
if [ -s "$HOME/.bash_profile" ]; then
    if ! grep -q "$VENVBURRITO_esc/startup.sh" $HOME/.bash_profile; then
        echo -e "\n\n# startup virtualenv-burrito\n. $VENVBURRITO_esc/startup.sh" >> ~/.bash_profile
    fi
else
    echo -e "# run .bashrc\n. ~/.bashrc\n\n# startup virtualenv-burrito\n. $VENVBURRITO_esc/startup.sh" > ~/.bash_profile
fi

echo
echo "Done with setup!"
echo
echo "The virtualenvwrapper environment will be available when you login."
echo
echo "To start it now, run this:"
echo "source $VENVBURRITO/startup.sh"
