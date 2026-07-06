@echo off
title Instalador Almox Bot
color 0A

echo ===================================================
echo    Instalador - Almox Bot
echo ===================================================
echo   Instalando: pywinauto openpyxl PyPDF2
echo.

REM Detecta Python
set "PY_EXE=python"
for %%v in (Python313 Python312 Python311 Python310 Python39 Python38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\%%v\python.exe" (
        set "PY_EXE=%LOCALAPPDATA%\Programs\Python\%%v\python.exe"
        goto found
    )
)
python --version >nul 2>&1
if %errorlevel% equ 0 goto found
echo ERRO: Python nao encontrado!
echo Execute instalar_dependencias.bat da pasta raiz primeiro.
pause
exit /b 1

:found
echo   Python: %PY_EXE%
echo.

echo   Atualizando o pip...
"%PY_EXE%" -m pip install --upgrade pip
echo.

echo   Instalando pywinauto (move mouse/teclado)...
"%PY_EXE%" -m pip install pywinauto
echo.

echo   Instalando openpyxl (gera o Excel)...
"%PY_EXE%" -m pip install openpyxl
echo.

echo   Instalando PyPDF2 (le o PDF)...
"%PY_EXE%" -m pip install PyPDF2
echo.

echo   Verificando...
"%PY_EXE%" -c "import pywinauto; import openpyxl; import PyPDF2; from pywinauto.keyboard import send_keys; print('OK! Todas as bibliotecas do bot presentes.')"

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo    TUDO PRONTO!
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo    ERRO NA INSTALACAO
    echo ===================================================
)
echo.
pause
