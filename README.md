# FL-Reader - Веб-библиотека для чтения книг

Веб-приложение для поиска, скачивания и чтения книг с интеграцией Флибусты.

## Требования

- Python 3.8+
- Tor (для доступа к .onion сайтам)

## Установка

1. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл и установите необходимые параметры:
```env
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

FLIBUSTA_ONION=http://flibustahezeous3.onion
TOR_PROXY_HOST=127.0.0.1
TOR_PROXY_PORT=9050
```

3. Активируйте виртуальное окружение:
```bash
source venv/bin/activate
```

4. Установите зависимости (если ещё не установлены):
```bash
pip install -r requirements.txt
```

5. Выполните миграции (если ещё не выполнены):
```bash
python manage.py migrate
```

6. Создайте суперпользователя для доступа к админ-панели:
```bash
python manage.py createsuperuser
```

## Запуск

1. Убедитесь, что Tor запущен и слушает на порту 9050:
```bash
brew install tor  # для macOS
tor
```

2. Запустите сервер разработки:
```bash
python manage.py runserver
```

3. Откройте браузер и перейдите по адресу:
```
http://127.0.0.1:8000/
```

## Структура проекта

```
fl-reader/
├── config/              # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/               # Основное приложение
│   ├── models.py        # Модель Book
│   ├── views.py         # Views для всех endpoints
│   ├── urls.py          # URL routing
│   ├── admin.py         # Админ-панель
│   ├── services/        # Бизнес-логика
│   │   ├── flibusta_service.py    # Работа с Флибустой через Tor
│   │   ├── fb2_parser.py          # Парсинг FB2 файлов
│   │   └── reading_service.py     # Управление чтением
│   └── templates/books/ # HTML шаблоны (базовые заглушки)
├── media/               # Загруженные файлы
│   ├── books/          # FB2 файлы
│   └── covers/         # Обложки книг
└── static/             # Статические файлы
    ├── css/
    └── js/
```

## API Endpoints

- `GET /` - Главная страница библиотеки
- `GET /book/<uuid>/` - Страница чтения книги
- `POST /book/<uuid>/progress/` - Сохранение прогресса чтения
- `GET /search/?q=<query>` - Поиск книг на Флибусте
- `POST /download/` - Скачивание книги с Флибусты
- `DELETE /book/<uuid>/delete/` - Удаление книги

## Конфигурация

Все настройки приложения управляются через переменные окружения в файле `.env`:

### Основные настройки
- `SECRET_KEY` - секретный ключ Django (обязательно)
- `DEBUG` - режим отладки (True/False)
- `ALLOWED_HOSTS` - список разрешенных хостов (через запятую)
- `DATABASE_NAME` - имя файла базы данных SQLite

### Настройки Флибусты и Tor
- `FLIBUSTA_ONION` - .onion адрес Флибусты
- `TOR_PROXY_HOST` - хост Tor SOCKS5 прокси
- `TOR_PROXY_PORT` - порт Tor SOCKS5 прокси

### Локализация
- `LANGUAGE_CODE` - код языка интерфейса (по умолчанию: ru-ru)
- `TIME_ZONE` - часовой пояс (по умолчанию: Europe/Moscow)

По умолчанию приложение использует SOCKS5 прокси на `127.0.0.1:9050`.
Убедитесь, что Tor запущен и доступен на этом порту.

## Разработка

Frontend шаблоны с HTMX, Alpine.js и Tailwind CSS будут добавлены отдельно.
Текущие шаблоны являются базовыми заглушками для тестирования backend.
