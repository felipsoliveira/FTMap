#!/bin/bash
# FTMap Enhanced Launcher Script for Linux/macOS
# Uso: ./ftmap.sh protein.pdb [argumentos...]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ para continuar."
    exit 1
fi

# Verificar se arquivo principal existe
if [ ! -f "ftmap_cli.py" ]; then
    echo "❌ ftmap_cli.py não encontrado no diretório atual."
    exit 1
fi

# Banner de boas-vindas
echo "🧬 FTMap Enhanced v2.0 - Sistema Modular de Análise de Druggability"
echo "=================================================================="

# Executar FTMap Enhanced
python3 ftmap_cli.py "$@"

# Capturar código de saída
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ FTMap Enhanced executado com sucesso!"
    echo "📁 Verifique os resultados no diretório de saída especificado."
else
    echo ""
    echo "❌ FTMap Enhanced terminou com erro (código: $exit_code)"
    echo "💡 Execute com --verbose para mais detalhes."
fi

exit $exit_code
