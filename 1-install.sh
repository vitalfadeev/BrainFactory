#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install pip --upgrade
pip install -r requirements.txt

django-admin startproject core .

mkdir core/batchs
./manage.py startapp batchs core/batchs
