if [[ -f /etc/bashrc ]]; then
  source /etc/bashrc
fi
if [[ -f /etc/bash.bashrc ]]; then
  source /etc/bash.bashrc
fi
if [[ -f ~/.bashrc ]]; then
  source ~/.bashrc
fi

# Reset PS1 so pexpect can find it
PS1="$"
