#!/bin/bash

./manage.py makemigrations batchs
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
