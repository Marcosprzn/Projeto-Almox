@echo off
title Almox Bot - Captura de Precos
color 0A

echo ===================================================
echo    Almox Bot - Captura de Prec,os
echo ===================================================
echo.

REM Detecta Python
set "PYTHON_EXE="

for %%v in (Python313 Python312 Python311 Python310 Python39 Python38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\%%v\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\%%v\python.exe"
        goto found
    )
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
    goto found
)

echo ERRO: Python nao encontrado!
pause
exit /b 1

:found
echo Python: %PYTHON_EXE%
echo.
echo Iniciando bot Almox...
echo.

powershell -Command "Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '%~dp0almox_bot.py' -Verb RunAs -Wait"

echo.
echo Bot finalizado.
pause
