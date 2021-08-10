#!/bin/sh -l

cd /github/workspace/

export PATH="/github/home/.local/bin:$PATH"

apt-get update && apt-get install -y inkscape build-essential \
    python-dev python3-dev libpq-dev

pip3 install --user --no-cache-dir -r requirements.txt
pip3 install --user --no-cache-dir pystan
pip3 install --user --no-cache-dir prophet

cd notebooks

mkdir -p output/html

jupyter nbconvert --to html --ExecutePreprocessor.kernel_name=python3 --execute *.ipynb --output-dir output/html
