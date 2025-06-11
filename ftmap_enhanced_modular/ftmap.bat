@echo off
REM FTMap Enhanced Launcher Script for Windows
REM Uso: ftmap.bat protein.pdb [argumentos...]

cd /d "%~dp0"

REM Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python 3.8+ para continuar.
    pause
    exit /b 1
)

REM Verificar se arquivo principal existe
if not exist "ftmap_cli.py" (
    echo ❌ ftmap_cli.py não encontrado no diretório atual.
    pause
    exit /b 1
)

REM Banner de boas-vindas
echo 🧬 FTMap Enhanced v2.0 - Sistema Modular de Análise de Druggability
echo ==================================================================

REM Executar FTMap Enhanced
python ftmap_cli.py %*

REM Verificar código de saída
if %errorlevel% equ 0 (
    echo.
    echo ✅ FTMap Enhanced executado com sucesso!
    echo 📁 Verifique os resultados no diretório de saída especificado.
) else (
    echo.
    echo ❌ FTMap Enhanced terminou com erro ^(código: %errorlevel%^)
    echo 💡 Execute com --verbose para mais detalhes.
)

pause
exit /b %errorlevel%
