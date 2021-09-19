FROM python:3.9.7-slim-bullseye

COPY . /src
WORKDIR /src
RUN pip3 install -r requirements.txt

CMD python3.9 main.py