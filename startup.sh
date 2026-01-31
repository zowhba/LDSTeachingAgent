#!/bin/bash

# Azure Web App 시작 스크립트
gunicorn --bind=0.0.0.0:8000 --workers=4 --worker-class=uvicorn.workers.UvicornWorker app_azure:app
