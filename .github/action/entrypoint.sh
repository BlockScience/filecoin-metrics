#!/bin/sh -l

cd /github/workspace/

export PATH="/github/home/.local/bin:$PATH"

apt-get update && apt-get install -y pandoc \
    texlive-xetex texlive-fonts-recommended \
    texlive-generic-recommended

pip3 install --user --no-cache-dir -r requirements.txt

cd notebooks

jupyter nbconvert --to pdf *.ipynb
