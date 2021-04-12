FROM python:3.8-alpine

WORKDIR /usr/src/app

RUN apk update \
    && apk add postgresql postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY /docker-app/entrypoint.sh /
RUN chmod +x /entrypoint.sh

RUN mkdir staticfiles
RUN mkdir logs

COPY . .


ENTRYPOINT ["/entrypoint.sh"]