#!/bin/sh

echo "starting app..."
uvicorn app:app --reload --host 0.0.0.0
