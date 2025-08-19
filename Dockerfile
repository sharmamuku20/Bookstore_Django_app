FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y gcc libpq-dev
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE 8000
RUN chmod +x /app/entrypoint.sh
# For Development
# CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# For Production
# Entrypoint runs collectstatic, migrate, then Gunicorn
ENTRYPOINT ["./entrypoint.sh"]
