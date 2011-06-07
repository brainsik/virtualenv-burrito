#!/bin/bash
#
# virtualenv-burrito
#
#   One command to have a working virtualenv + virtualenvwrapper environment.
#
set -e

VENVBURRITO="$HOME/.venvburrito"
VENVBURRITO_esc="\$HOME/.venvburrito"
MASTER_URL="https://raw.github.com/brainsik/virtualenv-burrito/master"

kernel=$(uname -s)
case "$kernel" in
    Darwin|Linux) ;;
    *) echo "Sadly, $kernel hasn't been tested. :'("; exit 1
esac

if [ -e "$VENVBURRITO" ]; then
    echo "Looks like virtualenv-burrito is already installed. Bye."
    exit 1
fi

if [ -s "$HOME/.bash_profile" ]; then
    if grep -q "$VENVBURRITO_esc/startup.sh" $HOME/.bash_profile; then
        echo "Looks like virtualenv-burrito is already installed. Bye."
        exit 1
    fi
fi


test -d $VENVBURRITO || mkdir -p $VENVBURRITO/{bin,lib/python}
test -d $HOME/.virtualenvs || mkdir $HOME/.virtualenvs

echo "Downloading virtualenv-burrito command"
curl $MASTER_URL/virtualenv-burrito.py > $VENVBURRITO/bin/virtualenv-burrito
chmod 755 $VENVBURRITO/bin/virtualenv-burrito
cmd="virtualenv-burrito upgrade firstrun"
echo -e "\nRunning: $cmd"
$VENVBURRITO/bin/$cmd
echo

# startup virtualenv-burrito in the bash_profile
start_code="\n# startup virtualenv-burrito\n. $VENVBURRITO_esc/startup.sh"
check_code="$VENVBURRITO_esc/startup.sh"
if [ -s ~/.bash_profile ]; then
    if ! grep -q "$check_code" ~/.bash_profile; then
        echo -e "$start_code" >> ~/.bash_profile
    fi
else
    if [ -s ~/.profile ]; then
        if ! grep -q "$check_code" ~/.profile; then
            echo -e "$start_code" >> ~/.profile
        fi
    else
        echo -e "# run .bashrc\n. ~/.bashrc\n$start_code" > ~/.bash_profile
    fi
fi

echo
echo "Done with setup!"
echo
echo "The virtualenvwrapper environment will be available when you login."
echo
echo "To start it now, run this:"
echo "source $VENVBURRITO/startup.sh"
