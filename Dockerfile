FROM python:3.13.2-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE $PORT

CMD gunicorn candBenchmark.wsgi:application --bind 0.0.0.0:$PORT
