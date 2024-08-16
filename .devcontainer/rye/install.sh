#!/usr/bin/env bash

set -e

echo "Activating feature 'rye'"

RYE_HOME="/home/vscode/.rye"

curl -sSf https://rye.astral.sh/get | RYE_HOME=$RYE_HOME RYE_INSTALL_OPTION="--yes" bash

echo 'source "$HOME/.rye/env"' >> /home/vscode/.zshrc

chown -R vscode $RYE_HOME

echo "Done!"
