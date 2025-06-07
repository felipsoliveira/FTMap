#!/usr/bin/env python3
"""
Análise para limpeza do workspace FTMap
Identifica arquivos essenciais vs desnecessários
"""

import os
import glob
from datetime import datetime

def analyze_ftmap_workspace():
    """Analisa workspace e categoriza arquivos"""
    
    print("="*70)
    print("🧹 ANÁLISE DE LIMPEZA DO WORKSPACE FTMAP")
    print("="*70)
    
    # Arquivos ESSENCIAIS (núcleo do sistema)
    essential_files = [
        "protein_raw.pdb",           # Proteína de entrada
        "protein.pdbqt",             # Proteína processada
        "probes.smi",                # Lista de fragmentos
        "parser_wrapper.py",         # Parser funcional
    ]
    
    # Diretórios ESSENCIAIS
    essential_dirs = [
        "probes/",                   # Fragmentos em PDB
        "probes_pdbqt/",            # Fragmentos em PDBQT
        "results/",                  # Resultados principais
        "organized_system/parsers/", # Parser correto
    ]
    
    # Arquivos de RESULTADO PRINCIPAL
    main_results = [
        "results/ftmap_protein_plus_hotspots.pdb",
        "results/ftmap_complete_molecules.pdb",
        "results/poses_probe_*_improved.pdbqt"
    ]
    
    # Arquivos DESNECESSÁRIOS (duplicados, experimentais, obsoletos)
    obsolete_files = []
    experimental_files = []
    
    # Verificar arquivos Python experimentais
    py_files = glob.glob("*.py")
    
    # Categorizar arquivos Python
    working_systems = []
    experimental_systems = []
    
    for py_file in py_files:
        if any(keyword in py_file for keyword in ['working', 'functional', 'complete']):
            working_systems.append(py_file)
        elif any(keyword in py_file for keyword in ['experimental', 'test', 'simple', 'quick', 'theoretical']):
            experimental_systems.append(py_file)
        elif 'ftmap_' in py_file and py_file not in ['ftmap_clustering_working.py']:
            experimental_systems.append(py_file)
    
    # Verificar diretórios redundantes
    redundant_dirs = []
    if os.path.exists("system_review") and os.path.exists("organized_system"):
        redundant_dirs.append("system_review")
    
    if os.path.exists("hotspots_output") and os.path.exists("organized_system/hotspots_output"):
        redundant_dirs.append("hotspots_output")
    
    # Contar fragmentos processados
    processed_fragments = len(glob.glob("results/poses_probe_*_improved.pdbqt"))
    
    # Relatório
    print(f"📊 SITUAÇÃO ATUAL:")
    print(f"   • Fragmentos processados: {processed_fragments}")
    print(f"   • Arquivos Python: {len(py_files)}")
    print(f"   • Sistemas funcionais: {len(working_systems)}")
    print(f"   • Sistemas experimentais: {len(experimental_systems)}")
    
    print(f"\n🟢 SISTEMAS FUNCIONAIS IDENTIFICADOS:")
    for system in working_systems:
        print(f"   ✅ {system}")
    
    print(f"\n🟡 SISTEMAS EXPERIMENTAIS (candidatos à remoção):")
    for system in experimental_systems:
        print(f"   🧪 {system}")
    
    print(f"\n🔴 DIRETÓRIOS REDUNDANTES:")
    for dir_name in redundant_dirs:
        print(f"   📁 {dir_name}")
    
    print(f"\n📋 RECOMENDAÇÕES DE LIMPEZA:")
    print(f"   1. Manter apenas 2-3 sistemas Python principais")
    print(f"   2. Remover {len(experimental_systems)} arquivos experimentais")
    print(f"   3. Consolidar diretórios redundantes")
    print(f"   4. Manter backups dos resultados principais")
    
    # Criar script de limpeza
    cleanup_script = f"""#!/bin/bash
# Script de limpeza automática do workspace FTMap
# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🧹 Iniciando limpeza do workspace FTMap..."

# Criar backup antes da limpeza
mkdir -p cleanup_backup
echo "📁 Criando backup..."

# Backup dos sistemas experimentais
"""
    
    for system in experimental_systems:
        cleanup_script += f"cp {system} cleanup_backup/ 2>/dev/null\n"
    
    cleanup_script += f"""
# Remover sistemas experimentais
echo "🗑️ Removendo sistemas experimentais..."
"""
    
    for system in experimental_systems:
        cleanup_script += f"rm -f {system}\n"
    
    cleanup_script += f"""
# Remover diretórios redundantes
echo "📁 Removendo diretórios redundantes..."
"""
    
    for dir_name in redundant_dirs:
        cleanup_script += f"rm -rf {dir_name}\n"
    
    cleanup_script += f"""
# Limpar cache Python
rm -rf __pycache__

echo "✅ Limpeza concluída!"
echo "📊 Workspace otimizado para produção"
echo "💾 Backup salvo em: cleanup_backup/"
"""
    
    with open("cleanup_workspace.sh", 'w') as f:
        f.write(cleanup_script)
    
    os.chmod("cleanup_workspace.sh", 0o755)
    
    print(f"\n✅ Análise concluída!")
    print(f"📄 Script de limpeza criado: cleanup_workspace.sh")
    print(f"🚀 Execute: ./cleanup_workspace.sh para limpar o workspace")

if __name__ == "__main__":
    analyze_ftmap_workspace()
