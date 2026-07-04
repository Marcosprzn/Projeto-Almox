@echo off
title Explorador de Grade MEGA ERP
color 0B

echo ===================================================
echo    Explorador de Grade do MEGA ERP
echo ===================================================
echo.

set "PYTHON_EXE="
for %%v in (Python313 Python312 Python311 Python310 Python39 Python38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\%%v\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\%%v\python.exe"
        goto found
    )
)
python --version >nul 2>&1
if %errorlevel% equ 0 ( set "PYTHON_EXE=python" & goto found )

echo ERRO: Python nao encontrado!
pause
exit /b 1

:found
echo Python: %PYTHON_EXE%
echo.
echo Iniciando explorador...
powershell -Command "Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '%~dp0explorar_grade.py' -Verb RunAs -Wait"
echo.
echo Finalizado.
pause
