#!make
#include .envs/.local/django.env
#include .envs/.local/postgres.env
#export $(shell sed 's/=.*//' .envs/.local/django.env)
#export $(shell sed 's/=.*//' .envs/.local/postgres.env)

MANAGE = python manage.py
SOURCE = src
MAIN = src
NAME = testb

PROJECT_DIR=$(shell pwd)
WSGI_PORT=8000


# ##########################################################################
# common commands
celerybeat:
	celery -A config.celery_app beat -l info
celeryworker:
	celery -A config.celery_app worker -l info
flower:
	celery flower \
		--app=config.celery_app \
		--broker="${CELERY_BROKER_URL}" \
		--basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"

up:
	docker-compose up

up+:
	docker-compose up --build

prune:
	docker system prune -a --volumes --force

startapp:
	mkdir $(SOURCE)/apps/$(NAME)
	sleep 3
	django-admin startapp $(NAME) ./$(SOURCE)/apps/$(NAME)

run:
	$(MANAGE) runserver 127.0.0.1:8001

# ##########################################################################
# deploy commands
gunicorn-run:
	$(MANAGE) collectstatic --no-input
	$(MANAGE) makemigrations --no-input
	$(MANAGE) migrate --no-input
	#cd $(PROJECT_DIR)/scr && gunicorn -w 4 -b 0.0.0.0:$(WSGI_PORT) config.wsgi --timeout 30 --log-level debug --max-requests 10000 --reload
	#gunicorn -w 4 -b 0.0.0.0:$(WSGI_PORT) config.config.wsgi:Application --timeout 30 --log-level debug --max-requests 10000 --reload
	#PYTHONPATH=`pwd` gunicorn config.wsgi -b 0.0.0.0:8000 --reload
	gunicorn config.wsgi -b 0.0.0.0:8000 --reload

collect:
	$(MANAGE) collectstatic --noinput

# ##########################################################################
# management
gen-users:
	$(MANAGE) gen_users

gen-s:
	$(MANAGE) gen_seances

kill-port:
	sudo fuser -k 8000/tcp

diagram:
	$(MANAGE) graph_models -a -g -o my_project_visualized.png

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

shell: # only after 'make extensions-install'
	$(MANAGE) shell_plus --print-sql

freeze:
	pip freeze > requirements.txt

# ##########################################################################
# Celery

worker:
	celery -A config.celery_app worker -l INFO

beat:
	cd $(SOURCE)/&& celery -A $(MAIN) beat -l info

worker-info:
	cd $(SOURCE) && celery -A $(MAIN) events

# ##########################################################################
# Uncommon commands

super:
	$(MANAGE) createsuperuser

install:
	pip install -r requirements.txt

check:
	$(MANAGE) check

migrations-dry:
	$(MANAGE) makemigrations --dry-run

gen-book-category:
	$(MANAGE) gen_book_category


# ##########################################################################
# Installations

flake8-install:
	pip install flake8
	pip install flake8-import-order # сортировку импортов
	pip install flake8-docstrings # доки есть и правильно оформлены
	pip install flake8-builtins # что в коде проекта нет переменных с именем из списка встроенных имён
	pip install flake8-quotes # проверять кавычки

	# ставим гит-хук
	flake8 --install-hook git
	git config --bool flake8.strict true

debugger-install:
	pip install django-debug-toolbar
	# 'debug_toolbar'                                    | add to the INSTALLED_APPS in settings.py
	# debug_toolbar.middleware.DebugToolbarMiddleware    | add to the MIDDLEWARE in settings.py
	# INTERNAL_IPS = [ "127.0.0.1", ]					 | create in the settings.py
	# path('__debug__/', include(debug_toolbar.urls))    | add to the urls.py in project DIR
	# import debug_toolbar                               | add to the urls.py in project DIR

extensions-install:
	pip install django-extensions
	pip install ipython
	# 'django_extensions'                                | add to the INSTALLED_APPS in settings.py

celery-install:
	pip install -U Celery
	pip install flower


# worker-info-web:
#	in basic console:
#   pip install flower
#   source venv/bin/activate
#	cd *my_proj*
#	celery -A *my_proj* flower

#	ps aux | grep celery
#   pkill -f csp_build.py   its a grep based kill

# signals
#        error_messages = {
#            NON_FIELD_ERRORS: {
#                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
#            },
#            'email_to': {
#                'required': "Email field is empty.",
#                'invalid': "Enter a valid email address.",
#            },
#        }
