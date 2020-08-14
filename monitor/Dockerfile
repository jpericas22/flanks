FROM python:3.8.5-alpine3.12

WORKDIR /src
COPY . .
RUN pip install -r deps.txt

CMD ["python", "main.py"]