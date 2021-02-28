FROM python:3

RUN mkdir /app
WORKDIR /app

COPY ../../requirements.txt .
RUN pip3 install --user --no-cache-dir -r requirements.txt

COPY ../../config .
COPY ../../filecoin_metrics .
COPY ../../notebooks .

RUN apt-get update && apt-get install -y pandoc \
    texlive-xetex texlive-fonts-recommended \
    texlive-generic-recommended

WORKDIR /app/notebooks

RUN jupyter nbconvert --to pdf *.ipynb
