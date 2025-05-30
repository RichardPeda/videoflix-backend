FROM python:3.12-alpine

LABEL maintainer="mihai@developerakademie.com"
LABEL version="1.0"
LABEL description="Python 3.14.0a7 Alpine 3.21"

WORKDIR /app

COPY . .



RUN apk update
RUN apk add --no-cache --upgrade bash
RUN apk add --no-cache postgresql-client
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN apk add --no-cache ffmpeg
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps
RUN chmod +x backend.entrypoint.sh

EXPOSE 8000

ENTRYPOINT [ "./backend.entrypoint.sh" ]
