FROM python:3.12.13-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN chmod +x prestart.sh 

ENTRYPOINT ["./prestart.sh"]
