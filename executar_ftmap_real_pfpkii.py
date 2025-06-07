#!/usr/bin/env python3
"""
Execução REAL do FTMap Enhanced com pfpkii.pdb
"""
import os
import sys
from pathlib import Path

# Adicionar caminho do src
sys.path.append('ftmap_enhanced_final/src')

from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm

def executar_ftmap_real():
    """Executa o FTMap Enhanced REAL com pfpkii.pdb"""
    
    print("🚀 EXECUTANDO FTMAP ENHANCED REAL - PFPKII.PDB")
    print("=" * 60)
    
    # Caminhos reais
    protein_file = "/home/murilo/girias/ftmapcaseiro/pfpkii.pdb"
    probes_dir = "/home/murilo/girias/ftmapcaseiro/probes_pdbqt"
    output_dir = "/home/murilo/girias/ftmapcaseiro/enhanced_outputs/execucao_real_pfpkii"
    
    # Criar diretório de saída
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"🧬 Proteína: {protein_file}")
    print(f"🔬 Probes: {probes_dir}")
    print(f"📁 Output: {output_dir}")
    
    # Inicializar e executar
    algorithm = FTMapEnhancedAlgorithm(protein_file=protein_file)
    
    print("\n🚀 INICIANDO ANÁLISE COMPLETA...")
    results = algorithm.run_enhanced_analysis(protein_file, probes_dir, output_dir)
    
    if results:
        print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print(f"📊 Resultados em: {output_dir}")
        return True
    else:
        print("\n❌ ANÁLISE FALHOU")
        return False

if __name__ == "__main__":
    executar_ftmap_real()
