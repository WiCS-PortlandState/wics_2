#!/usr/bin/env bash

git pull origin master 2> deploy_log.txt
pkill gunicorn
( cd .. ; . env_vars.sh )
( cd .. ; gunicorn --paste production.ini 2> logs.txt & ; disown )
service nginx restart