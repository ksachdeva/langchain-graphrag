#!/usr/bin/env bash

#echo "Configuring Rye"
#rye config --set-bool behavior.use-uv=true
#rye config --set-bool behavior.global-python=false

echo "changing zshrc theme to ys ..."
sed -i s/^ZSH_THEME=".\+"$/ZSH_THEME=\"ys\"/g ~/.zshrc    

echo "rye sync .."
rye sync