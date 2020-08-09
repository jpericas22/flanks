FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y gnupg

WORKDIR /src
COPY . .
RUN pip install -r deps.txt

CMD ["python", "main.py"]