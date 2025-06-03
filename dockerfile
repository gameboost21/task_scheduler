FROM python:alpine

WORKDIR /app

RUN apk add tzdata

RUN touch /etc/locatime

RUN ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime

COPY app/backend/requirements.txt .

RUN pip install -r requirements.txt

RUN apk add --no-cache bash

COPY app/backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--proxy-headers"]
