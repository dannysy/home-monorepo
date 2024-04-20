# Сервис аутентификации

# Настройка среды
## 1. Подготовка компьютера (если это еще происходило)
1. [Установить на машину PDM](https://pdm-project.org/en/latest/) 
2. Установить плагин для `.env`: `pdm self add pdm-dotenv`


## 2. Подготовка проекта
1. Запускаем терминал, заходим в папку проекта и устанавливаем зависимости (указаны в файле pyproject.toml) - `pdm install`
2. Указываем в PyCharm созданное окружение как интерпретатор этого проекта.

## 3. Подготовка БД
1. Скачать и установить docker. (Если еще не сделано)
2. Скачать образ Postgresql: `docker pull bitnami/postrgesql` (Если еще не сделано)
3. Создать .env (в папке data_base): `cp .env.example .env`
4. Настроить папку для Postgresql в корне проекта:  `mkdir -p cache/postgresql && sudo chown -R 1001:1001 cache/postgresql`