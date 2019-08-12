#!/bin/bash

cd /srv/www/htdocs/BrainFactory

git pull

source venv/bin/activate

pip install -r requirements.txt

./manage.py makemigrations
./manage.py migrate

service apache2 restart
