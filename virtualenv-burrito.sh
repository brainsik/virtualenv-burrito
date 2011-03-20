#!/bin/bash
#
# virtualenv-burrito
#
#   One command to have a working virtualenv + virtualenvwrapper environment.
#
set -e

VENVBURRITO="$HOME/.venvburrito"
VENVBURRITO_esc="\$HOME/.venvburrito"
GITHUB_URL="https://github.com/brainsik/virtualenv-burrito/raw/master"

kernel=$(uname -s)
case "$kernel" in
    Darwin|Linux) ;;
    *) echo "Sadly, $kernel hasn't been tested. :'("; exit 1
esac

if [ -s "$HOME/.bash_profile" ]; then
    if grep -q "$VENVBURRITO_esc/startup.sh" $HOME/.bash_profile; then
        echo "Looks like virtualenv-burrito is already installed. Bye."
        exit 1
    fi
fi


test -d $VENVBURRITO || mkdir -p $VENVBURRITO/{bin,lib}
test -d $HOME/.virtualenvs || mkdir $HOME/.virtualenvs

echo "Downloading venvburrito command"
curl $GITHUB_URL/venvburrito.py > $VENVBURRITO/bin/venvburrito
chmod 755 $VENVBURRITO/bin/venvburrito
echo -e "\nRunning: venvburrito update"
$VENVBURRITO/bin/venvburrito update
echo

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
        echo -e "\n# startup virtualenv-burrito\n. $VENVBURRITO_esc/startup.sh" >> ~/.bash_profile
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
