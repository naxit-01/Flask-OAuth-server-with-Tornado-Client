FROM python:3

WORKDIR /AuthServer

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV AUTHLIB_INSECURE_TRANSPORT=1

EXPOSE 5000
CMD [ "python", "./app.py" ]