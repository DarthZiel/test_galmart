# Тестовое для GALMART

роект реализует систему бронирования товаров с учетом времени жизни брони, админкой и API-доступом. Используется Django, DRF, PostgreSQL, Redis, MongoDB и Celery.


## Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/DarthZiel/test_galmart.git
cd test_galmart
```

2. Запустите проект:

```bash
docker-compose up --build -d
```

3. Примените миграции:

```bash
docker-compose exec web python manage.py migrate
```

4. 🔐 Создайте суперпользователя:

```bash
docker-compose exec web python manage.py createsuperuser
```

5. Проверьте работу:

- Админка: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/
- Документации: http://127.0.0.1:8000/swagger/

## Тестирование

1. Запуск тестов с покрытием:

```bash
docker-compose exec web coverage run -m pytest
docker-compose exec web coverage report
```
Тесты могут выполняться немного дольше обычного. Просто подождите, всё работает корректно.

2. HTML-отчет:

```bash
docker-compose exec web coverage html
```

Откройте `htmlcov/index.html` в браузере.

# Комментарии по тестовому заданию

## В вакансии и в тестовом не был явноуказан drf и пункт в тех. задании в тестовом "api интеграции" в начале меня немного запутал. Первая мысль была, что надо писать просто на django и добавить интеграции внешних api.
## Пункт про две базы данных. Я добавил Mongo, как базу для хранения логов, когда была совершена бронь, когда ее отменили или подтвердили
## Время жизни брони сделал настраиваемым: у каждой модели продукта есть поле reservation_timeout (в минутах), по умолчанию — 15 минут

## 📝 Автор

Нуржан Турегельдинов  
elegram: @DarthZiel

