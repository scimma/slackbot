FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY *.py /app

CMD ["python","bot.py"]

ENV PYTHONUNBUFFERED=1
