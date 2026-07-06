@echo off
title Instalador Completo Almox Bot
color 0A

echo ===================================================
echo    Instalador Completo - Almox Bot + OCR
echo ===================================================
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
echo Python: %PY_EXE%
echo.

REM ====================================================
REM PASSO 1: Instalar bibliotecas Python
REM ====================================================
echo [1/3] Instalando bibliotecas Python...
"%PY_EXE%" -m pip install openpyxl pypdf --quiet
echo.

REM ====================================================
REM PASSO 2: Baixar Tesseract OCR (portatil)
REM ====================================================
echo [2/3] Baixando Tesseract OCR...
set "TESS_DIR=%CD%\tesseract"
if not exist "%TESS_DIR%" mkdir "%TESS_DIR%"

REM Tenta baixar versao portatil do Tesseract
powershell -Command "$wc = New-Object System.Net.WebClient; $wc.DownloadFile('https://github.com/UB-Mannheim/tesseract/raw/main/tesseract.exe', '%TESS_DIR%\tesseract.exe')" >nul 2>&1

if not exist "%TESS_DIR%\tesseract.exe" (
    echo    Tesseract nao baixado. Baixe manualmente de:
    echo    https://github.com/UB-Mannheim/tesseract/wiki
    echo    Instale e adicione ao PATH.
    echo.
    echo    Pressione ENTER para continuar mesmo sem OCR...
    pause
) else (
    echo    Tesseract baixado para: %TESS_DIR%
    echo    Adicionando ao PATH...
    set "PATH=%TESS_DIR%;%PATH%"
)

echo.

REM ====================================================
REM PASSO 3: Verificar
REM ====================================================
echo [3/3] Verificando...
"%PY_EXE%" -c "import openpyxl; from pypdf import PdfReader; print('OK!')"
if errorlevel 1 (
    echo    Erro nas bibliotecas Python.
)

echo.
echo ===================================================
echo    Instalacao concluida!
echo ===================================================
echo.
pause
