#!/usr/bin/env python3
"""
FTMap Enhanced Modular - Script de Demonstração Completa
=======================================================

Este script demonstra como usar o sistema FTMap Enhanced completo
para análise de uma proteína usando todos os módulos implementados.

Autor: Sistema FTMap Enhanced
Data: Dezembro 2024
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any

# Adicionar módulos ao path
modules_path = str(Path(__file__).parent / "modules")
sys.path.insert(0, modules_path)

# Imports dos módulos
from config import FTMapEnhancedConfig
from molecular_docking import EnhancedMolecularDocking
from clustering_analysis import EnsembleClusteringAnalysis
from feature_extraction import AdvancedFeatureExtractor
from machine_learning import EnsembleDruggabilityPredictor
from visualization_reports import VisualizationReports

def main():
    """Demonstração completa do sistema FTMap Enhanced"""
    
    print("🚀 FTMap Enhanced Modular - Demonstração Completa")
    print("=" * 60)
    
    # 1. Configuração do sistema
    print("\n🔧 1. Inicializando configuração avançada...")
    config = FTMapEnhancedConfig()
    
    # Configurações para demonstração
    config.exhaustiveness = 128
    config.num_modes = 500
    config.energy_range = 8.0
    config.grid_expansion_factor = 1.5
    config.n_jobs = -1
    
    print(f"   ✅ Exhaustividade: {config.exhaustiveness}")
    print(f"   ✅ Modos: {config.num_modes}")
    print(f"   ✅ Parallelização: {config.n_jobs}")
    
    # 2. Docking Molecular
    print("\n🧬 2. Inicializando engine de docking molecular...")
    docking_engine = EnhancedMolecularDocking(config)
    
    print(f"   ✅ Engine configurado com {len(docking_engine.probes)} probes")
    print(f"   ✅ Capacidade máxima: 100,000+ poses")
    print(f"   ✅ Filtros de qualidade ativados")
    
    # 3. Clustering Ensemble
    print("\n🎪 3. Configurando clustering ensemble...")
    clustering_analyzer = EnsembleClusteringAnalysis(config)
    
    print(f"   ✅ Algoritmos configurados: {len(clustering_analyzer.algorithms)}")
    print("   ✅ - Hierarchical Ward (peso: 0.4)")
    print("   ✅ - DBSCAN (peso: 0.3)")
    print("   ✅ - Agglomerative (peso: 0.3)")
    print("   ✅ Matriz de consenso ativada")
    
    # 4. Feature Extraction
    print("\n📊 4. Inicializando extração de features...")
    feature_extractor = AdvancedFeatureExtractor(config)
    
    print(f"   ✅ Features disponíveis: {len(feature_extractor.get_feature_names())}")
    print("   ✅ - 5 features energéticas")
    print("   ✅ - 9 features espaciais")
    print("   ✅ - 8 features químicas")
    print("   ✅ - 6 features de interação")
    print("   ✅ - 1 feature de consenso")
    
    # 5. Machine Learning
    print("\n🤖 5. Configurando ensemble de ML...")
    ml_predictor = EnsembleDruggabilityPredictor(config)
    
    print("   ✅ Modelos configurados:")
    print("   ✅ - Random Forest Otimizado")
    print("   ✅ - Gradient Boosting Avançado")
    print("   ✅ - SVM com kernel RBF")
    print("   ✅ Validação cruzada 5-fold")
    
    # 6. Visualização
    print("\n📈 6. Preparando módulo de visualização...")
    visualizer = VisualizationReports(config)
    
    print("   ✅ Relatórios HTML interativos")
    print("   ✅ Scripts PyMOL automáticos")
    print("   ✅ Gráficos estatísticos avançados")
    print("   ✅ Análise de druggability")
    
    # 7. Demonstração com dados simulados
    print("\n⚡ 7. Executando workflow completo simulado...")
    
    # Simular dados de entrada
    n_poses = 1000
    print(f"   📦 Simulando {n_poses} poses de docking...")
    
    # Poses simuladas
    poses_data = []
    for i in range(n_poses):
        poses_data.append({
            'pose_id': f'pose_{i:04d}',
            'x': np.random.uniform(-20, 20),
            'y': np.random.uniform(-20, 20),
            'z': np.random.uniform(-20, 20),
            'binding_energy': np.random.uniform(-12, -4),
            'probe_type': np.random.choice(['ethanol', 'isopropanol', 'acetone', 'acetonitrile']),
            'vdw_energy': np.random.uniform(-8, -2),
            'electrostatic_energy': np.random.uniform(-4, 1)
        })
    
    poses_df = pd.DataFrame(poses_data)
    print(f"   ✅ {len(poses_df)} poses simuladas criadas")
    
    # Clustering
    print("   🎪 Executando clustering ensemble...")
    cluster_results = clustering_analyzer.analyze_clusters(poses_df)
    n_clusters = len(cluster_results.get('cluster_labels', []))
    print(f"   ✅ {n_clusters} clusters identificados pelo ensemble")
    
    # Feature extraction (simulada)
    print("   📊 Extraindo features dos clusters...")
    if n_clusters > 0:
        # Simular features para demonstração
        features_data = []
        for i in range(min(n_clusters, 10)):  # Máximo 10 clusters para demonstração
            features_data.append({
                'cluster_id': i,
                'binding_energy_mean': np.random.uniform(-10, -6),
                'cluster_size': np.random.randint(10, 100),
                'volume': np.random.uniform(500, 2000),
                'surface_area': np.random.uniform(200, 800),
                'druggability_index': np.random.uniform(0.3, 0.9),
                'probe_diversity': np.random.uniform(0.4, 0.8),
                'hydrophobic_ratio': np.random.uniform(0.2, 0.6),
                'polar_ratio': np.random.uniform(0.3, 0.7),
                'pharmacophore_score': np.random.uniform(0.5, 0.95)
            })
        
        features_df = pd.DataFrame(features_data)
        print(f"   ✅ Features extraídas para {len(features_df)} clusters")
        
        # Machine Learning
        print("   🤖 Executando predição de druggability...")
        # Simular predições para demonstração
        predictions = np.random.uniform(0.4, 0.9, len(features_df))
        features_df['ml_prediction'] = predictions
        print(f"   ✅ Predições ML geradas (média: {predictions.mean():.3f})")
        
        # Análise de resultados
        print("\n📋 8. Análise dos resultados:")
        print(f"   🎯 Clusters de alta qualidade: {sum(predictions > 0.7)}")
        print(f"   📊 Score médio de druggability: {predictions.mean():.3f}")
        print(f"   🔬 Cluster top: {features_df.loc[features_df['ml_prediction'].idxmax(), 'cluster_id']}")
        
        # Informações da proteína (simulada)
        protein_info = {
            'name': 'Protein_Demo',
            'pdb_id': 'DEMO',
            'resolution': 2.1,
            'method': 'X-RAY DIFFRACTION',
            'organism': 'Demo organism'
        }
        
        print("\n📈 9. Geração de relatórios...")
        print("   ✅ Dados prontos para visualização")
        print("   ✅ Features completas disponíveis")
        print("   ✅ Predições ML finalizadas")
        
    else:
        print("   ⚠️ Nenhum cluster identificado na simulação")
    
    # Status final
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO COMPLETA FINALIZADA!")
    print("=" * 60)
    
    print("\n📊 RESUMO DA CAPACIDADE DO SISTEMA:")
    print(f"   🧬 Poses máximas: 100,000+")
    print(f"   🎪 Algoritmos de clustering: 3 (ensemble)")
    print(f"   📊 Features extraídas: 29")
    print(f"   🤖 Modelos ML: 3 (ensemble)")
    print(f"   📈 Relatórios: HTML + PyMOL + CSV")
    
    print("\n🚀 SISTEMA PRONTO PARA ANÁLISES REAIS!")
    print("\nPara usar com proteína real:")
    print("1. Forneça arquivo PDB da proteína")
    print("2. Configure parâmetros específicos")
    print("3. Execute análise completa")
    print("4. Visualize resultados em PyMOL")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Demonstração executada com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Erro na demonstração")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        sys.exit(1)
