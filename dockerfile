FROM python:alpine

WORKDIR /app

COPY app/backend/requirements.txt .

RUN pip install -r requirements.txt

COPY app/backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
