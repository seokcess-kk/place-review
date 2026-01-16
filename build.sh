#!/bin/bash
set -e

echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "Installing and building frontend..."
cd frontend
npm install
npm run build
