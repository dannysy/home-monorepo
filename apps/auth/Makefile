
# Инициализация
export DIR := $(realpath .)
## Creating .env file from template, if file not exists
ifeq ("$(wildcard $(DIR)/.env)","")
	RSP1 := $(shell cp -v $(DIR)/.env_example $(DIR)/.env)
endif
include $(DIR)/.env

default: help

# Установка инструментария для mac
init-macos: 
	@if [ $(shell which pipx) = "" ]; then\
		brew install pipx;\
		pipx ensurepath;\
		sudo pipx ensurepath --global;\
	fi
	@if [ $(shell which poetry) = "" ]; then\
		pipx install poetry;\
	fi
	@if [ $(shell which black) = "" ]; then\
		pipx install black;\
	fi
	@if [ $(shell which docker) = "" ]; then\
		echo "go to https://docs.docker.com/desktop/install/mac-install/ to install docker";\
	fi
.PHONY: init-macos

# Зависимости
dep:
	@poetry install
.PHONY: dep

# Запуск виртуального окружения
venv:
	@poetry shell
.PHONY: venv

# Форматирование кодовой базы
fmt:
	@black .
.PHONY: fmt

# Линтеры
lint:
	@flake8
.PHONY: lint

# Запуск служб в докер контейнерах (окружения)
# Важно:
# Если приложение запускается в контейнере обратите внимание что конфигурация должна быть соответствующей
dk-start:
	docker network create $(DOCKER_NET)

	# Postgres
	docker run --rm --name $(SERVICE_NAME)-postgres --net $(DOCKER_NET) \
	-p 5434:5432 \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_PASSWORD=postgres \
	-e POSTGRES_DB=$(SERVICE_NAME) \
	-d postgres:14

	# Redis
	docker run --rm --name $(SERVICE_NAME)-redis --net $(DOCKER_NET) \
	-p 6378:6379 \
	-d redis

.PHONY: dk-start

# Остановка запущенных служб (окружения)
dk-stop:
	docker stop $(SERVICE_NAME)-postgres
	docker stop $(SERVICE_NAME)-redis
	docker network rm $(DOCKER_NET)
.PHONY: dk-stop


# Создать новую миграцию (make NAME=my_migration_name_here mig-new)
mig-new:
	@alembic revision --message="$(NAME)" --autogenerate
.PHONY: mig-new

# Миграция на одну позицию назад
mig-dn:
	@alembic downgrade head
.PHONY: mig-dn

# Миграция вперёд до конца
mig-up:
	@alembic upgrade head
.PHONY: mig-up

# Help
h:
	@echo "Usage: make [target]"
	@echo "  target is:"
	@echo "  init-macos	    - "Установка инструментария для mac"
	@echo "         dep	    - Обновление зависимостей"
	@echo "        venv	    - Запуск виртуального окружения"
	@echo "         fmt	    - Форматирование кодовой базы"
	@echo "        lint	    - Линтеры"
	@echo "      test-u	    - Unit тесты"
	@echo "      test-i	    - Интеграционные тесты"
	@echo "      test-b	    - Тесты производительности"
	@echo "      test		- Запуск всех тестов"
	@echo "         run	    - Запуск в режиме разработки"
	@echo "         dev	    - Запуск в режиме отладки"
	@echo "     mig-new	    - Создание новой миграции (make mig-new NAME=my_migration_name_here)"
	@echo "      mig-dn	    - Миграция на одну позицию назад"
	@echo "      mig-up	    - Миграция вперёд до конца"
	@echo "    dk-start	    - Запуск служб в докер контейнерах (окружения)"
	@echo "     dk-stop	    - Остановка запущенных служб (окружения)"
	@echo "         dki	    - Создание docker образа"
	@echo "         dkr	    - Запуск сервиса в докер контейнере"
.PHONY: h
help: h
.PHONY: help