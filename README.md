# home-monorepo

# Настройка среды
## 1. Подготовка компьютера
1. [Установить на машину PDM](https://pdm-project.org/en/latest/) 
2. Установить плагин для `.env`: `pdm self add pdm-dotenv`

## 2. Подготовка проекта
1. Клонируем репозиторий
2. Запускаем терминал, заходим в папку проекта и устанавливаем зависимости (указаны в файле pyproject.toml) - `pdm install`
3. Указываем в PyCharm созданное окружение как интерпретатор этого проекта.

## 3. Подготовка БД
1. Скачать и установить docker.
2. Скачать образ Postgresql: `docker pull bitnami/postrgesql`
3. Создать .env (в папке data_base): `cp .env.example .env`
4. Настроить папку для Postgresql в корне проекта:  `mkdir -p cache/postgresql && sudo chown -R 1001:1001 cache/postgresql`