#!/usr/bin/env bash

git pull origin master >> deploy_log.txt
service nginx restart
service gunicorn restart