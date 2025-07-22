@echo off
title Misure-mq Complete Build and Distribution
color 0B

echo.
echo ========================================
echo   Misure-mq Complete Build System
echo ========================================
echo.

echo Questo script eseguira':
echo 1. Build dell'applicazione desktop
echo 2. Creazione pacchetti di distribuzione
echo 3. Preparazione asset per GitHub
echo.

pause

echo.
echo [1/3] Avvio build dell'applicazione...
echo ========================================
python build_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Errore durante il build!
    pause
    exit /b 1
)

echo.
echo [2/3] Creazione pacchetti di distribuzione...
echo ========================================
python create_distribution.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Errore durante la creazione dei pacchetti!
    pause
    exit /b 1
)

echo.
echo [3/3] Riepilogo finale...
echo ========================================

echo.
echo ✅ Build completato con successo!
echo.
echo 📁 File generati:
echo    - dist\Misure-mq.exe (eseguibile principale)
echo    - dist\installer.bat (installer per utenti)
echo    - Misure-mq_v2.0_*.zip (pacchetto distribuzione)
echo    - github_release_assets\ (asset per GitHub)
echo.

echo 🚀 L'applicazione e' pronta per la distribuzione!
echo.
echo 📋 Prossimi passi:
echo    1. Testa l'eseguibile su un sistema pulito
echo    2. Carica i file su GitHub Release
echo    3. Distribuisci agli utenti finali
echo.

pause