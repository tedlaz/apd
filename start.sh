#!/bin/sh
gunicorn --bind 0.0.0.0:8001 wsgi:app
