#!/bin/bash
#
# virtualenv-burrito
#
#   One command to have a working virtualenv + virtualenvwrapper environment.
#
set -e

VENVBURRITO="$HOME/.venvburrito"
VENVBURRITO_esc="\$HOME/.venvburrito"
MASTER_URL="https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master"

if [ -e "$VENVBURRITO" ]; then
    echo "Found existing $VENVBURRITO"
    echo
    echo "Looks like virtualenv-burrito is already installed. Bye."
    exit 1
fi

kernel=$(uname -s)
case "$kernel" in
    Darwin|Linux|FreeBSD) ;;
    *) echo "Sadly, $kernel hasn't been tested. :'("; exit 1
esac

# provide a friendly way to set this environment variable
test "$1" = "--exclude-profile" && exclude_profile="yep"


backup_profile() {
    profile="$1"
    cp -p $HOME/$profile $HOME/${profile}.pre-virtualenv-burrito
}

write_simple_startup() {
    profile="$1"
    cat >> ~/$profile <<EOF

# startup virtualenv-burrito
if [ -f $VENVBURRITO_esc/startup.sh ]; then
    . $VENVBURRITO_esc/startup.sh
fi
EOF
}

modify_profile() {
    # startup virtualenv-burrito when the shell starts
    echo
    unset profile
    start_code="\n# startup virtualenv-burrito\n. $VENVBURRITO_esc/startup.sh"
    check_code="$VENVBURRITO_esc/startup.sh"

    # check for bash and zsh profiles
    if [ -n "$BASH_VERSION" ] && [ -e ~/.bash_profile ]; then
        if ! grep -q "$check_code" ~/.bash_profile; then
            profile=".bash_profile"
            backup_profile $profile
            write_simple_startup $profile
        fi
    elif [ -n "$ZSH_VERSION" ] && [ -e ~/.zprofile ]; then
        if ! grep -q "$check_code" ~/.zprofile; then
            profile=".zprofile"
            backup_profile $profile
            write_simple_startup $profile
        fi
    elif [ -n "$ZSH_VERSION" ]; then
        profile=".zprofile"
        write_simple_startup $profile
    elif [ -n "$BASH_VERSION" ] && [ -s ~/.profile ]; then
        if ! grep -q "$check_code" ~/.profile; then
            profile=".profile"
            backup_profile $profile
            # match the .profile style and wrap paths in double quotes
            cat >> ~/$profile <<EOF

# if running bash
if [ -n "\$BASH_VERSION" ]; then
    # startup virtualenv-burrito
    if [ -f "$VENVBURRITO_esc/startup.sh" ]; then
        . "$VENVBURRITO_esc/startup.sh"
    fi
fi
EOF
        fi
    elif [ -n "$BASH_VERSION" ]; then
        profile=".bash_profile"
        cat > ~/$profile <<EOF
# startup virtualenv-burrito
if [ -f $VENVBURRITO_esc/startup.sh ]; then
. $VENVBURRITO_esc/startup.sh
fi

# include .bashrc if it exists
if [ -f \$HOME/.bashrc ]; then
. \$HOME/.bashrc
fi
EOF
    else
        echo "Your shell profile could not be detected."
        echo "Please contact @brainsik on Twitter or GitHub."
    fi
}


pyver=$(python -c 'import platform;print ".".join(platform.python_version().split(".")[:2])')
mkdir -p $VENVBURRITO/{bin,libexec,lib/python$pyver/site-packages}
test -d $HOME/.virtualenvs || mkdir $HOME/.virtualenvs

echo "Downloading virtualenv-burrito command"
curl $MASTER_URL/virtualenv-burrito.py > $VENVBURRITO/bin/virtualenv-burrito
chmod 755 $VENVBURRITO/bin/virtualenv-burrito
cmd="virtualenv-burrito upgrade firstrun"
echo -e "\nRunning: $cmd"
$VENVBURRITO/bin/$(echo $cmd)

unset profile
test -z "$exclude_profile" && modify_profile
if [ -n "$profile" ]; then
    if [ -e $HOME/${profile}.pre-virtualenv-burrito ]; then
        backup=" The original\nwas saved to ~/$profile.pre-virtualenv-burrito."
    fi
    echo
    echo "Code was added to $HOME/$profile so the virtualenvwrapper"
    echo -e "environment will be available when you login.$backup"
fi

echo
echo "Done with setup!"
echo
echo "To start now, run this:"
echo "source $VENVBURRITO/startup.sh"
