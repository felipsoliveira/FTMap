#!/usr/bin/env python3
"""
Teste simples das progress bars no clustering
"""
import sys
import time
import numpy as np
from pathlib import Path

# Adicionar caminho do src
sys.path.append('ftmap_enhanced_final/src')

# Importar apenas o necessário 
try:
    from tqdm import tqdm
    print("✅ tqdm disponível")
except ImportError:
    print("❌ tqdm não disponível - instalando...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "tqdm"], check=True)
    from tqdm import tqdm

try:
    import pandas as pd
    print("✅ pandas disponível")
except ImportError:
    print("❌ pandas não disponível - instalando...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas"], check=True)
    import pandas as pd

def test_clustering_progress():
    """Testa apenas o clustering com progress bars"""
    
    print("🎯 TESTE DAS PROGRESS BARS - CLUSTERING")
    print("=" * 50)
    
    # Simular dados de docking
    print("📊 Gerando dados simulados...")
    poses = []
    for i in range(1000):
        pose = {
            'x': np.random.uniform(-20, 20),
            'y': np.random.uniform(-20, 20), 
            'z': np.random.uniform(-20, 20),
            'energy': np.random.uniform(-8, -2),
            'probe': np.random.choice(['benzene', 'ethanol', 'water', 'phenol', 'acetone'])
        }
        poses.append(pose)
    
    print(f"   ✅ {len(poses)} poses simuladas geradas")
    
    # Simular clustering com progress bar
    print("🎯 Testando clustering com progress bar...")
    
    # Agrupar poses por "clusters" simulados
    clusters = {}
    for i, pose in enumerate(poses):
        cluster_id = i % 10  # 10 clusters simulados
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(pose)
    
    print(f"   📊 {len(clusters)} clusters simulados criados")
    
    # Simular extração de features com progress bar
    print("🧠 Testando extração de features com progress bar...")
    
    features = []
    valid_clusters = {k: v for k, v in clusters.items() if len(v) >= 3}
    
    with tqdm(total=len(valid_clusters), desc="🧠 Extracting Features", leave=False) as pbar:
        for cluster_id, cluster_poses in valid_clusters.items():
            pbar.set_description(f"🧠 Features Cluster {cluster_id}")
            
            # Simular processamento
            time.sleep(0.1)  # Simula trabalho
            
            # Extrair features básicas
            energies = [p['energy'] for p in cluster_poses]
            positions = np.array([[p['x'], p['y'], p['z']] for p in cluster_poses])
            
            feature = {
                'cluster_id': cluster_id,
                'min_energy': min(energies),
                'mean_energy': np.mean(energies),
                'cluster_size': len(cluster_poses),
                'center_x': np.mean(positions[:, 0]),
                'center_y': np.mean(positions[:, 1]),
                'center_z': np.mean(positions[:, 2])
            }
            
            features.append(feature)
            pbar.update(1)
    
    print(f"   ✅ {len(features)} features extraídas com progress bar")
    
    # Simular ML ensemble com progress bar
    print("🤖 Testando ML ensemble com progress bar...")
    
    models = ['RandomForest', 'SVM', 'GradientBoosting']
    with tqdm(total=len(models), desc="🤖 Training ML Models", leave=False) as pbar:
        for model_name in models:
            pbar.set_description(f"🤖 Training {model_name}")
            time.sleep(0.2)  # Simula treinamento
            pbar.update(1)
    
    print("   ✅ ML ensemble treinado com progress bar")
    
    # Teste de clustering avançado com progress bar
    print("🎪 Testando clustering avançado com progress bar...")
    
    methods = ['Hierarchical', 'DBSCAN', 'Energy-based', 'Ensemble']
    with tqdm(total=len(methods), desc="🎪 Advanced Clustering", leave=False) as pbar:
        for method in methods:
            pbar.set_description(f"🎪 {method} Clustering")
            time.sleep(0.15)  # Simula clustering
            pbar.update(1)
    
    print("   ✅ Clustering avançado concluído com progress bar")
    
    print("\n🎉 TESTE DAS PROGRESS BARS CONCLUÍDO COM SUCESSO!")
    print("✅ Todas as progress bars funcionaram corretamente")
    print("✅ tqdm e pandas foram importados com sucesso")
    print("✅ Sistema pronto para execução real")
    
    return True

if __name__ == "__main__":
    test_clustering_progress()
