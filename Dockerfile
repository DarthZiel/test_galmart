FROM python:3.10-slim

WORKDIR /app

# Копируем файлы зависимостей для кэширования
COPY pyproject.toml uv.lock /app/

# Устанавливаем UV и зависимости глобально
RUN pip install uv \
    && uv pip compile pyproject.toml -o requirements.txt \
    && uv pip install --system --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY . /app

# Открываем порт для Gunicorn
EXPOSE 8000

# Запускаем Gunicorn с правильным WSGI-модулем
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]