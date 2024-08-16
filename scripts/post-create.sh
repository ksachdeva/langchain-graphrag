#!/usr/bin/env bash

#echo "Configuring Rye"
#rye config --set-bool behavior.use-uv=true
#rye config --set-bool behavior.global-python=false

USERNAME=vscode

echo "changing zshrc theme to ys ..."
sed -i s/^ZSH_THEME=".\+"$/ZSH_THEME=\"ys\"/g ~/.zshrc

echo "sym link zsh_history ..."
mkdir -p /commandhistory
touch /commandhistory/.zsh_history
chown -R $USERNAME /commandhistory

SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.zsh_history"
echo "$SNIPPET" >> "/home/$USERNAME/.zshrc"

echo "rye sync .."
rye sync
