FROM python:3.9.9

# Copy local code to the container image.
WORKDIR /app
COPY . /app

RUN pip install --default-timeout=100 -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
