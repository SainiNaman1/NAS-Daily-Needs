@echo off
title NAS Daily Needs - POS & Retail ERP
cd /d "%~dp0NAS-Daily-Needs" 2>nul || cd /d "%~dp0"
python app.py
if errorlevel 1 (
    echo.
    echo An error occurred while running the application.
    pause
)
