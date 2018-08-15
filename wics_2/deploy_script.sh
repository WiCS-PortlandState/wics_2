#!/usr/bin/env bash

git pull origin master >> deploy_log.txt
pkill gunicorn
( cd .. ; gunicorn --paste production.ini 2> logs.txt )
service nginx restart