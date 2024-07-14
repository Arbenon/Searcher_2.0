# Використовуємо офіційний образ Python версії 3.9
FROM python:3.9

# Встановлюємо залежності, які потрібні для виконання вашої програми
RUN apt-get update \
    && apt-get install -y \
        libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Створюємо робочу директорію для нашого додатка
WORKDIR /app

# Копіюємо файли з поточної директорії в робочу директорію контейнера
COPY . .

# Встановлюємо необхідні Python пакети з requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуску вашої програми при старті контейнера
CMD ["python", "./searcher2.0.py"]

