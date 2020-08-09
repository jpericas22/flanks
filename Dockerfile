FROM python:latest
WORKDIR /src
RUN pip install -r dependencies.txt
COPY . .
CMD ["", ""]
