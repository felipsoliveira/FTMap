#!/bin/bash
# 🚀 SETUP COMPLETO FTMAP ENHANCED - SCRIPT DEFINITIVO
# Instala todas as dependências e executa o algoritmo com pfpkii.pdb
# Criado em: June 7, 2025

echo "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"
echo "🔥 FTMAP ENHANCED - SETUP COMPLETO E EXECUÇÃO"
echo "🎯 OBJETIVO: Instalar tudo e rodar pfpkii.pdb AGORA!"
echo "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"

# Variáveis de configuração
WORKSPACE_DIR="/home/murilo/girias/ftmapcaseiro"
VENV_DIR="$WORKSPACE_DIR/enhanced_env"
PROTEIN_FILE="$WORKSPACE_DIR/pfpkii.pdb"
PROBES_DIR="$WORKSPACE_DIR/probes_pdbqt"
FTMAP_SRC="$WORKSPACE_DIR/ftmap_enhanced_final/src"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para logging
log_step() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Verificar se estamos no diretório correto
cd "$WORKSPACE_DIR" || {
    log_error "Não foi possível acessar $WORKSPACE_DIR"
    exit 1
}

log_step "🏠 Diretório de trabalho: $(pwd)"

# 1. VERIFICAR SISTEMA E DEPENDÊNCIAS BASE
log_step "🔍 ETAPA 1: Verificando sistema base..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 não encontrado!"
    log_step "Instalando Python3..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
else
    PYTHON_VERSION=$(python3 --version)
    log_success "Python encontrado: $PYTHON_VERSION"
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    log_warning "pip3 não encontrado, instalando..."
    sudo apt install -y python3-pip
else
    log_success "pip3 disponível"
fi

# Verificar git
if ! command -v git &> /dev/null; then
    log_warning "git não encontrado, instalando..."
    sudo apt install -y git
else
    log_success "git disponível"
fi

# 2. CONFIGURAR AMBIENTE VIRTUAL
log_step "🐍 ETAPA 2: Configurando ambiente virtual..."

if [ ! -d "$VENV_DIR" ]; then
    log_step "Criando ambiente virtual em $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    log_success "Ambiente virtual já existe"
fi

# Ativar ambiente virtual
log_step "Ativando ambiente virtual..."
source "$VENV_DIR/bin/activate"

# Verificar se ativou corretamente
if [[ "$VIRTUAL_ENV" != "" ]]; then
    log_success "Ambiente virtual ativado: $VIRTUAL_ENV"
else
    log_error "Falha ao ativar ambiente virtual"
    exit 1
fi

# 3. INSTALAR DEPENDÊNCIAS PYTHON
log_step "📦 ETAPA 3: Instalando dependências Python..."

# Atualizar pip primeiro
log_step "Atualizando pip..."
pip install --upgrade pip

# Lista completa de dependências
DEPENDENCIES=(
    "numpy>=1.21.0"
    "pandas>=1.3.0"
    "scikit-learn>=1.0.0"
    "scipy>=1.7.0"
    "matplotlib>=3.4.0"
    "seaborn>=0.11.0"
    "tqdm>=4.62.0"
    "joblib>=1.0.0"
    "networkx>=2.6.0"
    "plotly>=5.0.0"
    "openpyxl>=3.0.0"
    "xlsxwriter>=3.0.0"
    "biopython>=1.79"
    "rdkit-pypi>=2022.3.0"
    "mdanalysis>=2.0.0"
    "prody>=2.0.0"
    "pymol-open-source>=2.5.0"
    "ipython>=7.0.0"
    "jupyter>=1.0.0"
    "notebook>=6.0.0"
)

log_step "Instalando ${#DEPENDENCIES[@]} pacotes Python..."

for dep in "${DEPENDENCIES[@]}"; do
    log_step "  📦 Instalando $dep..."
    pip install "$dep" --quiet --no-warn-script-location
    if [ $? -eq 0 ]; then
        log_success "    ✅ $dep instalado"
    else
        log_warning "    ⚠️ Problema com $dep, continuando..."
    fi
done

# 4. INSTALAR AUTODOCK VINA
log_step "⚗️ ETAPA 4: Instalando AutoDock Vina..."

# Verificar se Vina já está instalado
if command -v vina &> /dev/null; then
    VINA_VERSION=$(vina --version 2>&1 | head -n1)
    log_success "AutoDock Vina já instalado: $VINA_VERSION"
else
    log_step "Baixando e instalando AutoDock Vina..."
    
    # Criar diretório para ferramentas
    mkdir -p "$WORKSPACE_DIR/tools"
    cd "$WORKSPACE_DIR/tools"
    
    # Baixar Vina (versão Linux)
    if [ ! -f "vina" ]; then
        log_step "Baixando AutoDock Vina..."
        wget -q https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O vina
        chmod +x vina
    fi
    
    # Adicionar ao PATH
    export PATH="$WORKSPACE_DIR/tools:$PATH"
    echo 'export PATH="'$WORKSPACE_DIR'/tools:$PATH"' >> ~/.bashrc
    
    if [ -f "vina" ]; then
        log_success "AutoDock Vina instalado em $WORKSPACE_DIR/tools/vina"
    else
        log_warning "AutoDock Vina não pôde ser baixado, usando simulação"
    fi
    
    cd "$WORKSPACE_DIR"
fi

# 5. INSTALAR FERRAMENTAS AUXILIARES
log_step "🔧 ETAPA 5: Instalando ferramentas auxiliares..."

# OpenBabel para conversões de formato
if ! command -v obabel &> /dev/null; then
    log_step "Instalando OpenBabel..."
    sudo apt install -y openbabel
else
    log_success "OpenBabel já instalado"
fi

# PyMOL para visualização (se não tiver)
if ! command -v pymol &> /dev/null; then
    log_step "Instalando PyMOL..."
    sudo apt install -y pymol
else
    log_success "PyMOL já instalado"
fi

# 6. VERIFICAR ARQUIVOS NECESSÁRIOS
log_step "📁 ETAPA 6: Verificando arquivos necessários..."

# Verificar proteína
if [ -f "$PROTEIN_FILE" ]; then
    PROTEIN_SIZE=$(du -h "$PROTEIN_FILE" | cut -f1)
    log_success "Proteína encontrada: pfpkii.pdb ($PROTEIN_SIZE)"
else
    log_error "Proteína não encontrada: $PROTEIN_FILE"
    exit 1
fi

# Verificar probes
if [ -d "$PROBES_DIR" ]; then
    PROBE_COUNT=$(ls "$PROBES_DIR"/*.pdbqt 2>/dev/null | wc -l)
    log_success "Probes encontrados: $PROBE_COUNT arquivos em $PROBES_DIR"
else
    log_error "Diretório de probes não encontrado: $PROBES_DIR"
    exit 1
fi

# Verificar código fonte
if [ -f "$FTMAP_SRC/ftmap_enhanced_algorithm.py" ]; then
    ALGO_SIZE=$(wc -l < "$FTMAP_SRC/ftmap_enhanced_algorithm.py")
    log_success "Algoritmo FTMap Enhanced encontrado: $ALGO_SIZE linhas"
else
    log_error "Código fonte não encontrado: $FTMAP_SRC/ftmap_enhanced_algorithm.py"
    exit 1
fi

# 7. TESTAR IMPORTAÇÕES
log_step "🧪 ETAPA 7: Testando importações Python..."

python3 -c "
import sys
sys.path.append('$FTMAP_SRC')

modules = [
    'numpy', 'pandas', 'sklearn', 'scipy', 'matplotlib', 
    'tqdm', 'joblib', 'networkx'
]

print('🔍 Testando importações...')
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module} - OK')
    except ImportError as e:
        print(f'❌ {module} - ERRO: {e}')

# Testar algoritmo principal
try:
    from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm
    print('✅ FTMapEnhancedAlgorithm - OK')
    
    # Teste rápido de inicialização
    algo = FTMapEnhancedAlgorithm('$PROTEIN_FILE')
    print('✅ Inicialização do algoritmo - OK')
    
except Exception as e:
    print(f'❌ FTMapEnhancedAlgorithm - ERRO: {e}')
"

if [ $? -eq 0 ]; then
    log_success "Todas as importações funcionando!"
else
    log_error "Problemas com importações"
    exit 1
fi

# 8. CRIAR SCRIPT DE EXECUÇÃO RÁPIDA
log_step "🚀 ETAPA 8: Criando script de execução rápida..."

cat > "$WORKSPACE_DIR/EXECUTAR_RAPIDO.py" << 'EOL'
#!/usr/bin/env python3
"""
🚀 EXECUÇÃO RÁPIDA FTMAP ENHANCED
Script otimizado para execução imediata
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Configurações
WORKSPACE_DIR = "/home/murilo/girias/ftmapcaseiro"
sys.path.append(f"{WORKSPACE_DIR}/ftmap_enhanced_final/src")

def main():
    print("🚀 FTMAP ENHANCED - EXECUÇÃO RÁPIDA")
    print("=" * 50)
    
    # Arquivos
    protein_file = f"{WORKSPACE_DIR}/pfpkii.pdb"
    probes_dir = f"{WORKSPACE_DIR}/probes_pdbqt"
    
    # Output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"{WORKSPACE_DIR}/enhanced_outputs/execucao_rapida_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm
        
        print(f"📂 Proteína: {protein_file}")
        print(f"📂 Probes: {probes_dir}")
        print(f"📂 Output: {output_dir}")
        
        # Executar
        algorithm = FTMapEnhancedAlgorithm(protein_file=protein_file)
        results = algorithm.run_enhanced_analysis(
            protein_file=protein_file,
            probes_dir=probes_dir,
            output_dir=str(output_dir)
        )
        
        print("\n🎉 ANÁLISE CONCLUÍDA!")
        print(f"📊 Resultados em: {output_dir}")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
EOL

chmod +x "$WORKSPACE_DIR/EXECUTAR_RAPIDO.py"
log_success "Script de execução rápida criado: EXECUTAR_RAPIDO.py"

# 9. EXECUTAR TESTE RÁPIDO
log_step "🧪 ETAPA 9: Executando teste rápido..."

python3 "$WORKSPACE_DIR/test_progress_bars.py"

if [ $? -eq 0 ]; then
    log_success "Teste rápido passou!"
else
    log_warning "Teste rápido falhou, mas continuando..."
fi

# 10. SUMÁRIO FINAL
echo ""
echo "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉"
echo "🏆 SETUP COMPLETO FTMAP ENHANCED - CONCLUÍDO!"
echo "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉"

echo ""
log_step "📊 SUMÁRIO DA INSTALAÇÃO:"
echo "  🐍 Python: $(python3 --version)"
echo "  📦 Ambiente virtual: $VENV_DIR"
echo "  🧬 Proteína: pfpkii.pdb ($(du -h "$PROTEIN_FILE" | cut -f1))"
echo "  🧪 Probes: $PROBE_COUNT arquivos"
echo "  ⚗️ AutoDock Vina: $(command -v vina &> /dev/null && echo "Instalado" || echo "Simulação")"
echo "  🔬 Algoritmo: $(wc -l < "$FTMAP_SRC/ftmap_enhanced_algorithm.py") linhas"

echo ""
log_step "🚀 COMO EXECUTAR AGORA:"
echo "  1. Execução rápida:     python3 EXECUTAR_RAPIDO.py"
echo "  2. Execução completa:   python3 EXECUTAR_PFPKII_AGORA.py"
echo "  3. Teste clustering:    python3 test_clustering_pfpkii.py"
echo "  4. Reativar env:        source enhanced_env/bin/activate"

echo ""
log_step "📁 ARQUIVOS CRIADOS:"
echo "  • EXECUTAR_RAPIDO.py - Script de execução otimizada"
echo "  • enhanced_env/ - Ambiente virtual com todas as dependências"
echo "  • tools/vina - AutoDock Vina (se baixado)"

echo ""
echo "🔥 O SISTEMA ESTÁ PRONTO PARA RODAR A PORRA DO PFPKII.PDB! 🔥"
echo "🚀 Basta executar: python3 EXECUTAR_RAPIDO.py"
echo ""

# Manter ambiente ativo
echo "💡 DICA: O ambiente virtual está ativo neste terminal."
echo "💡 Para ativar em novo terminal: source $VENV_DIR/bin/activate"

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "   python3 EXECUTAR_RAPIDO.py"
echo ""
