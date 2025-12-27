# 🚀 Деплой Lumina Reader

Инструкция по развертыванию проекта на production сервере с использованием Docker и Caddy.

## 📋 Требования

- Docker и Docker Compose установлены на сервере
- Домен s6ptember.online настроен и указывает на ваш сервер (A-запись)
- Порты 80 и 443 открыты в файерволе

## 🔧 Настройка

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd fl-reader
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

Заполните необходимые переменные:

```bash
# Сгенерируйте новый SECRET_KEY
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Основные настройки
DEBUG=False
ALLOWED_HOSTS=s6ptember.online,www.s6ptember.online
CSRF_TRUSTED_ORIGINS=https://s6ptember.online,https://www.s6ptember.online

# База данных
DATABASE_NAME=db.sqlite3

# Локализация
LANGUAGE_CODE=ru-ru
TIME_ZONE=Europe/Moscow

# Flibusta (настройте Tor отдельно)
FLIBUSTA_ONION=http://flibustahezeous3.onion
TOR_PROXY_HOST=127.0.0.1
TOR_PROXY_PORT=9050
```

### 3. Создание базы данных

```bash
# Создайте пустой файл базы данных
touch db.sqlite3
chmod 664 db.sqlite3
```

### 4. Сборка и запуск

```bash
# Сборка образов
docker-compose build

# Запуск контейнеров в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### 5. Инициализация базы данных

```bash
# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сбор статики (если нужно)
docker-compose exec web python manage.py collectstatic --noinput
```

## 🔐 Безопасность

### Настроенные меры безопасности:

- ✅ HTTPS с автоматическими сертификатами Let's Encrypt (Caddy)
- ✅ HSTS с preload
- ✅ Secure cookies (session, CSRF)
- ✅ XSS и Content-Type защита
- ✅ Запрет на iframe (X-Frame-Options: DENY)
- ✅ Read-only контейнеры
- ✅ Минимальные привилегии (no-new-privileges)
- ✅ Dropped capabilities (ALL + только NET_BIND_SERVICE)
- ✅ Не-root пользователь в контейнере
- ✅ Оптимизация SQLite (WAL mode, cache, timeouts)

### Firewall настройки:

```bash
# UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## 📊 Мониторинг

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только Django
docker-compose logs -f web

# Только Caddy
docker-compose logs -f caddy
```

### Статус сервисов

```bash
docker-compose ps
```

### Health check

```bash
# Проверка здоровья контейнера
docker inspect lumina-web --format='{{.State.Health.Status}}'

# Автоматически выполняется каждые 30 секунд
```

## 🔄 Обновление

```bash
# Остановка сервисов
docker-compose down

# Получение изменений
git pull

# Пересборка (если изменились зависимости)
docker-compose build

# Применение миграций
docker-compose run --rm web python manage.py migrate

# Запуск
docker-compose up -d
```

## 🗄️ Бэкапы

### База данных

```bash
# Создание бэкапа
docker-compose exec web sqlite3 /app/db.sqlite3 ".backup '/app/backup.db'"
docker cp lumina-web:/app/backup.db ./backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Восстановление из бэкапа
docker cp ./backups/db_backup.sqlite3 lumina-web:/app/db.sqlite3
docker-compose restart web
```

### Медиа файлы

```bash
# Создание архива
docker-compose exec web tar -czf /tmp/media_backup.tar.gz -C /app media/
docker cp lumina-web:/tmp/media_backup.tar.gz ./backups/media_$(date +%Y%m%d_%H%M%S).tar.gz
```

## 🔧 Управление

### Остановка

```bash
docker-compose stop
```

### Запуск

```bash
docker-compose start
```

### Перезапуск

```bash
docker-compose restart
```

### Полная очистка

```bash
# ВНИМАНИЕ: Удаляет все данные!
docker-compose down -v
```

## 📝 Полезные команды

### Django команды

```bash
# Django shell
docker-compose exec web python manage.py shell

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Проверка проекта
docker-compose exec web python manage.py check
```

### Работа с контейнерами

```bash
# Вход в контейнер
docker-compose exec web sh

# Просмотр процессов
docker-compose top

# Использование ресурсов
docker stats
```

## 🌐 SSL сертификаты

Caddy автоматически получает и обновляет SSL сертификаты от Let's Encrypt.

Сертификаты хранятся в Docker volume `caddy_data`.

### Проверка сертификата

```bash
openssl s_client -connect s6ptember.online:443 -servername s6ptember.online < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

## 🐛 Troubleshooting

### Проблемы с HTTPS

1. Убедитесь, что домен корректно настроен (A-запись)
2. Проверьте, что порты 80 и 443 открыты
3. Посмотрите логи Caddy: `docker-compose logs caddy`

### База данных заблокирована

SQLite использует WAL mode для улучшения параллелизма. Если возникают блокировки:

```bash
docker-compose exec web python manage.py shell
>>> from django.db import connection
>>> connection.cursor().execute("PRAGMA journal_mode=WAL;")
```

### Недостаточно памяти

Увеличьте количество workers в Dockerfile:

```dockerfile
CMD ["gunicorn", "config.wsgi:application", "--workers", "2", ...]
```

## 📞 Поддержка

При возникновении проблем проверьте:

1. Логи контейнеров: `docker-compose logs`
2. Статус здоровья: `docker-compose ps`
3. Доступность портов: `netstat -tulpn | grep -E ':(80|443)'`
4. DNS настройки: `dig s6ptember.online`

---

**Проект готов к production использованию! 🎉**
