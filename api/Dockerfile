FROM python:3.8-slim-buster

EXPOSE 5000

WORKDIR /src
COPY . .
RUN pip install -r deps.txt

CMD ["python", "main.py"]