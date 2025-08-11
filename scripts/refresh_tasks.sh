#!/bin/bash

# Celery beat 시작 스크립트
echo "Starting Celery beat scheduler..."

celery -A config purge
