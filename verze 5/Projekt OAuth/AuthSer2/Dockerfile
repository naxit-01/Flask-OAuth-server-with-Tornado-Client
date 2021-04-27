
# syntax=docker/dockerfile:1
FROM python:3.5.2
WORKDIR /AuthSer

ENV FLASK_ENV=development
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=False

COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000

COPY . .
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug

ENV AUTHLIB_INSECURE_TRANSPORT=1
CMD flask run

