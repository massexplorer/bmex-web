# syntax=docker/dockerfile:1

FROM python:3.9-slim-bullseye

RUN mkdir wd
WORKDIR wd
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "gunicorn", "--workers=8", "--threads=4", "-b 0.0.0.0:80", "app:server"]
