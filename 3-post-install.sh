#!/bin/bash

./manage.py makemigrations baths
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
