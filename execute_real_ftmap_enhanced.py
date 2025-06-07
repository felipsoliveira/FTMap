#!/usr/bin/env python3
"""
Execução REAL do FTMap Enhanced Algorithm
Análise completa do pfpkii.pdb com todas as funcionalidades avançadas
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def main():
    """Executa análise FTMap Enhanced REAL completa"""
    
    print("🚀 EXECUTANDO FTMAP ENHANCED - ANÁLISE REAL COMPLETA")
    print("=" * 80)
    
    # Adicionar o diretório src ao path
    workspace = Path("/home/murilo/girias/ftmapcaseiro")
    src_path = workspace / "ftmap_enhanced_final" / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm
        print("✅ Módulo FTMapEnhancedAlgorithm importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return False
    
    # Definir caminhos
    protein_file = workspace / "pfpkii.pdb"
    probes_dir = workspace / "probes_pdbqt"
    
    # Criar diretório de saída com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = workspace / "enhanced_outputs" / f"real_analysis_complete_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Proteína: {protein_file}")
    print(f"📁 Probes: {probes_dir}")
    print(f"📁 Output: {output_dir}")
    
    # Verificar arquivos
    if not protein_file.exists():
        print(f"❌ Erro: Proteína não encontrada em {protein_file}")
        return False
    
    if not probes_dir.exists():
        print(f"❌ Erro: Diretório de probes não encontrado em {probes_dir}")
        return False
    
    probe_files = list(probes_dir.glob("*.pdbqt"))
    if not probe_files:
        print(f"❌ Erro: Nenhum probe PDBQT encontrado em {probes_dir}")
        return False
    
    print(f"✅ Proteína verificada: {protein_file.stat().st_size:,} bytes")
    print(f"✅ Probes verificados: {len(probe_files)} arquivos")
    
    try:
        # Inicializar algoritmo
        print("\n🧬 Inicializando FTMap Enhanced Algorithm...")
        algorithm = FTMapEnhancedAlgorithm(protein_file=str(protein_file))
        
        # Executar análise completa
        print("\n🚀 INICIANDO ANÁLISE FTMAP ENHANCED COMPLETA...")
        print("   Esta análise pode levar alguns minutos...")
        
        results = algorithm.run_enhanced_analysis(
            protein_file=str(protein_file),
            probes_dir=str(probes_dir),
            output_dir=str(output_dir)
        )
        
        print(f"\n✅ ANÁLISE REAL CONCLUÍDA COM SUCESSO!")
        print(f"📊 Resultados salvos em: {output_dir}")
        
        if results:
            print(f"🎯 Clusters analisados: {results.get('total_clusters', 'N/A')}")
            print(f"🎯 Clusters alta druggabilidade: {results.get('high_druggability_clusters', 'N/A')}")
            print(f"🎯 Hotspots excepcionais: {results.get('exceptional_hotspots', 'N/A')}")
            if 'average_druggability' in results:
                print(f"🎯 Druggabilidade média: {results['average_druggability']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na execução: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 EXECUÇÃO REAL COMPLETADA COM SUCESSO!")
        sys.exit(0)
    else:
        print("\n💥 EXECUÇÃO FALHADA!")
        sys.exit(1)
