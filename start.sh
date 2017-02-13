#!/bin/bash

while ! nc -z rabbitmq 5672; do sleep 1; done
python run.py start *:*
