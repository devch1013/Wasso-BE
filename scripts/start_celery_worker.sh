#!/bin/bash

# Celery worker 시작 스크립트
echo "Starting Celery worker..."

celery -A config worker --loglevel=info --concurrency=4 