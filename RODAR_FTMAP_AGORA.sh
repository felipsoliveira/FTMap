#!/bin/bash
# 🚀 EXECUÇÃO RÁPIDA FTMAP ENHANCED (dependências já instaladas)
# Para usar quando o setup já foi executado

echo "🚀 FTMAP ENHANCED - EXECUÇÃO RÁPIDA"
echo "=================================="

WORKSPACE_DIR="/home/murilo/girias/ftmapcaseiro"
VENV_DIR="$WORKSPACE_DIR/enhanced_env"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$WORKSPACE_DIR" || exit 1

# Ativar ambiente virtual se existir
if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}🐍 Ativando ambiente virtual...${NC}"
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ Ambiente ativo: $VIRTUAL_ENV${NC}"
else
    echo "⚠️ Ambiente virtual não encontrado, usando Python do sistema"
fi

# Verificar arquivos principais
echo -e "${BLUE}📁 Verificando arquivos...${NC}"
echo "  📄 pfpkii.pdb: $([ -f pfpkii.pdb ] && echo "✅" || echo "❌")"
echo "  📂 probes_pdbqt: $([ -d probes_pdbqt ] && echo "✅ ($(ls probes_pdbqt/*.pdbqt 2>/dev/null | wc -l) probes)" || echo "❌")"
echo "  🧠 Algorithm: $([ -f ftmap_enhanced_final/src/ftmap_enhanced_algorithm.py ] && echo "✅" || echo "❌")"

echo ""
echo "🚀 OPÇÕES DE EXECUÇÃO:"
echo "======================================"
echo "1️⃣  python3 EXECUTAR_PFPKII_AGORA.py     # Execução principal"
echo "2️⃣  python3 test_clustering_pfpkii.py     # Teste do clustering"
echo "3️⃣  python3 test_progress_bars.py         # Teste das progress bars"
echo "4️⃣  python3 EXECUTAR_RAPIDO.py            # Execução otimizada (se existir)"

echo ""
echo "🎯 RECOMENDADO PARA RODAR AGORA:"
echo "python3 EXECUTAR_PFPKII_AGORA.py"
echo ""

# Auto-executar se solicitado
if [ "$1" = "--auto" ]; then
    echo "🚀 Executando automaticamente..."
    python3 EXECUTAR_PFPKII_AGORA.py
fi

# Mostrar status do ambiente
echo "📊 STATUS DO AMBIENTE:"
echo "  🐍 Python: $(python3 --version)"
echo "  📦 Virtual Env: $([ "$VIRTUAL_ENV" != "" ] && echo "Ativo" || echo "Inativo")"
echo "  💾 Working Dir: $(pwd)"
echo ""
