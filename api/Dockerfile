FROM python:3.8.5-alpine3.12

WORKDIR /src
COPY . .
RUN pip install -r deps.txt
RUN tar zxf dockerize-alpine-linux-amd64-v0.6.1.tar.gz

CMD ["python", "main.py"]