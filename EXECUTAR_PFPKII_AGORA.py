#!/usr/bin/env python3
"""
🚀 EXECUÇÃO DIRETA DA PFPKII.PDB COM FTMAP ENHANCED
Vai rodar a PORRA toda agora! 😄
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar src do enhanced
sys.path.append('/home/murilo/girias/ftmapcaseiro/ftmap_enhanced_final/src')

def main():
    print("🚀" * 50)
    print("🔥 EXECUTANDO PFPKII.PDB NO FTMAP ENHANCED - AGORA!")
    print("🚀" * 50)
    
    # Arquivos
    protein_file = "/home/murilo/girias/ftmapcaseiro/pfpkii.pdb"
    probes_dir = "/home/murilo/girias/ftmapcaseiro/probes_pdbqt"
    
    # Output com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"/home/murilo/girias/ftmapcaseiro/enhanced_outputs/execucao_real_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 Proteína: {protein_file}")
    print(f"📂 Probes: {probes_dir}")
    print(f"📂 Output: {output_dir}")
    
    # Verificar arquivos
    if not Path(protein_file).exists():
        print(f"❌ Proteína não encontrada: {protein_file}")
        return False
        
    if not Path(probes_dir).exists():
        print(f"❌ Probes não encontrados: {probes_dir}")
        return False
    
    probe_files = list(Path(probes_dir).glob("*.pdbqt"))
    print(f"✅ {len(probe_files)} probes encontrados")
    
    try:
        # Importar e inicializar
        print("📦 Carregando FTMap Enhanced Algorithm...")
        from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm
        
        algorithm = FTMapEnhancedAlgorithm(protein_file=protein_file)
        print("✅ Algoritmo carregado!")
        
        # EXECUTAR ANÁLISE COMPLETA
        print("\n🚀 INICIANDO ANÁLISE COMPLETA...")
        
        results = algorithm.run_enhanced_analysis(
            protein_file=protein_file,
            probes_dir=probes_dir,
            output_dir=str(output_dir)
        )
        
        print("\n🎉 ANÁLISE CONCLUÍDA COM SUCESSO!")
        print(f"📊 Resultados salvos em: {output_dir}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("🔧 Tentando instalar dependências...")
        
        # Instalar dependências necessárias
        import subprocess
        packages = ['tqdm', 'pandas', 'scikit-learn', 'scipy']
        
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"✅ {package} instalado")
            except:
                print(f"❌ Erro instalando {package}")
        
        print("🔄 Tentando novamente...")
        return main()  # Tentar novamente
        
    except Exception as e:
        print(f"❌ ERRO DURANTE EXECUÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏆 SUCESSO TOTAL!")
    else:
        print("\n💥 FALHA NA EXECUÇÃO")
    
    sys.exit(0 if success else 1)
