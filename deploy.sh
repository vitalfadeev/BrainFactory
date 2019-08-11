#!/bin/#!/usr/bin/env sh

source venv/bin/activate

pip install -r requirements.txt

./manage.py makemigrations
./manage.py migrate

service apache2 restart
