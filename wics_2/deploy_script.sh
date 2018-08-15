#!/usr/bin/env bash

git pull origin master >> deploy_log.txt
( cd .. ; gunicorn --paste production.ini 2> logs.txt )
service nginx restart