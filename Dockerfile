FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# коп весь проект
COPY . .

# папка для логов
RUN mkdir -p /app/logs

RUN chmod -R 777 /app/logs /app

CMD ["python", "bot.py"]