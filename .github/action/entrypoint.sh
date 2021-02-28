#!/bin/sh -l

cd /github/workspace/

pip3 install --user --no-cache-dir -r requirements.txt

apt-get update && apt-get install -y pandoc \
    texlive-xetex texlive-fonts-recommended \
    texlive-generic-recommended

cd notebooks

jupyter nbconvert --to pdf *.ipynb
