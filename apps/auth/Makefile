
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

# Форматирование кодовой базы
fmt:
	@black .
.PHONY: fmt

# Линтеры
lint:
	@flake8
.PHONY: lint

# Help
h:
	@echo "Usage: make [target]"
	@echo "  target is:"
	@echo "  init-macos	    - "Установка инструментария для mac"
	@echo "         dep	    - Обновление зависимостей"
	@echo "         fmt	    - Форматирование кодовой базы"
	@echo "        lint	    - Линтеры"
	@echo "      test-u	    - Unit тесты"
	@echo "      test-i	    - Интеграционные тесты"
	@echo "      test-b	    - Тесты производительности"
	@echo "      test		- Запуск всех тестов"
	@echo "         run	    - Запуск в режиме разработки"
	@echo "         dev	    - Запуск в режиме отладки"
	@echo "      mig-st	    - Статус миграции"
	@echo "      mig-dn	    - Миграция на одну позицию назад"
	@echo "      mig-up	    - Миграция вперёд до конца"
	@echo "   mig-reset	    - Миграция назад до конца (сброс всех миграций)"
	@echo "    dk-start	    - Запуск служб в докер контейнерах (окружения)"
	@echo "     dk-stop	    - Остановка запущенных служб (окружения)"
	@echo "         dki	    - Создание docker образа"
	@echo "         dkr	    - Запуск сервиса в докер контейнере"
.PHONY: h
help: h
.PHONY: help