#!/usr/bin/env python3
"""
Teste específico do algoritmo enhanced com progress bars
"""
import os
import sys
from pathlib import Path

# Adicionar caminho do src
sys.path.append('ftmap_enhanced_final/src')

from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm

def test_enhanced_algorithm():
    """Testa o algoritmo enhanced com todas as progress bars"""
    
    print("🧪 TESTE DO ALGORITMO ENHANCED COM PROGRESS BARS")
    print("=" * 60)
    
    # Configurar caminhos
    protein_file = "/home/murilo/girias/ftmapcaseiro/pfpkii.pdb"
    probes_dir = "/home/murilo/girias/ftmapcaseiro/probes_pdbqt"
    output_dir = "/home/murilo/girias/ftmapcaseiro/ftmap_enhanced_final/test_progress_bars"
    
    # Verificar arquivos
    if not Path(protein_file).exists():
        print(f"❌ Proteína não encontrada: {protein_file}")
        return False
        
    if not Path(probes_dir).exists():
        print(f"❌ Probes não encontrados: {probes_dir}")
        return False
    
    # Criar diretório de saída
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Inicializar algoritmo
        print("🚀 Inicializando FTMap Enhanced Algorithm...")
        algorithm = FTMapEnhancedAlgorithm(protein_file=protein_file)
        
        # Executar análise completa
        print("🔬 Executando análise enhanced completa...")
        results = algorithm.run_enhanced_analysis(protein_file, probes_dir, output_dir)
        
        if results:
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print(f"📊 Resultados salvos em: {output_dir}")
            return True
        else:
            print("❌ TESTE FALHOU - Sem resultados")
            return False
            
    except Exception as e:
        print(f"❌ ERRO DURANTE TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_algorithm()
    sys.exit(0 if success else 1)
