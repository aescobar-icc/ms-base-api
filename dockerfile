FROM python:3.8-slim-bullseye



WORKDIR /api-run
COPY . /api-run

RUN pip install --no-cache-dir -r /api-run/requirements.txt

#RUN ash /api-run/sh/install_libs.sh

#RUN apk del .build-deps


ENTRYPOINT gunicorn --conf /api-run/server_conf.py server:app --reload
