# syntax=docker/dockerfile:1

FROM python:3.9-slim-bullseye
SHELL ["/bin/bash", "-c"]

RUN mkdir wd
WORKDIR wd

COPY . .

ARG TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then ARCHITECTURE=amd64; elif [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then ARCHITECTURE=arm; elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then ARCHITECTURE=aarch64; else ARCHITECTURE=amd64; fi \
    && cp "utils/rmf_rbm_${ARCHITECTURE}.so" "utils/rmf_rbm_hybrid.so" /

COPY requirements.txt .
RUN pip3 install -r requirements.txt

CMD [ "gunicorn", "--workers=8", "--threads=4", "-b 0.0.0.0:80", "app:server"]
