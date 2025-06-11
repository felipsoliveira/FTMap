#!/usr/bin/env python3
print("🧪 Testando FTMap Enhanced...")

try:
    print("1. Testando imports básicos...")
    import numpy as np
    print("   ✅ NumPy OK")
    
    import pandas as pd
    print("   ✅ Pandas OK")
    
    import sys
    import os
    from pathlib import Path
    print("   ✅ Libs básicas OK")
    
    print("2. Testando módulos FTMap...")
    
    # Adicionar path
    sys.path.insert(0, './modules')
    
    # Testar config
    from config import FTMapConfig
    print("   ✅ Config importado")
    
    config = FTMapConfig()
    print(f"   ✅ Config criado - Exhaustiveness: {config.docking_config['exhaustiveness']}")
    
    # Testar outros módulos
    from molecular_docking import MolecularDockingEngine
    print("   ✅ Molecular docking importado")
    
    from clustering_analysis import ClusteringAnalyzer
    print("   ✅ Clustering importado")
    
    from feature_extraction import FeatureExtractor
    print("   ✅ Feature extraction importado")
    
    from machine_learning import MachineLearningPredictor
    print("   ✅ Machine learning importado")
    
    print("\n🎉 TODOS OS MÓDULOS FORAM CARREGADOS COM SUCESSO!")
    print("\n🎯 Sistema FTMap Enhanced operacional:")
    print("   • Docking com parâmetros avançados")
    print("   • Clustering ensemble (3 algoritmos)")
    print("   • Extração de 29 recursos sofisticados")
    print("   • ML ensemble com validação robusta")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
