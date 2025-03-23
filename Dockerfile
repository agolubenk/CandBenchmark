FROM python:3.13.2-alpine

WORKDIR /app

RUN apk update && apk add --no-cache dcron

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
