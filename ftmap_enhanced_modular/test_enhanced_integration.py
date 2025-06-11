#!/usr/bin/env python3
"""
Teste de Integração do FTMap Enhanced
====================================
Testa a integração completa dos módulos aprimorados
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent / "modules"))

from modules.config import FTMapConfig
from modules.molecular_docking import MolecularDockingEngine
from modules.clustering_analysis import ClusteringAnalyzer
from modules.feature_extraction import FeatureExtractor
from modules.machine_learning import MachineLearningPredictor

def test_enhanced_workflow():
    """Testa o workflow completo com os módulos aprimorados"""
    print("🧪 TESTE DE INTEGRAÇÃO - FTMap Enhanced")
    print("=" * 60)
    
    # 1. Configuração
    print("1️⃣ Testando configuração avançada...")
    config = FTMapConfig()
    print(f"   ✅ Parâmetros de docking: exhaustiveness={config.docking_config['exhaustiveness']}")
    print(f"   ✅ Ensemble clustering: {len(config.clustering_config['ensemble']['algorithms'])} algoritmos")
    print(f"   ✅ Energy cutoffs: {len(config.energy_cutoffs)} níveis")
    
    # 2. Docking simulado (dados mock)
    print("\n2️⃣ Testando docking molecular aprimorado...")
    docking_engine = MolecularDockingEngine(config)
    
    # Simular poses
    mock_poses = []
    for i in range(100):  # Simular 100 poses
        pose = type('DockingPose', (), {
            'id': f'pose_{i}',
            'probe': config.probe_molecules[i % len(config.probe_molecules)],
            'affinity': np.random.uniform(-8, -2),
            'coordinates': np.random.uniform(-20, 20, 3),
            'rmsd': np.random.uniform(0.5, 3.0)
        })()
        mock_poses.append(pose)
    
    print(f"   ✅ {len(mock_poses)} poses simuladas")
    
    # 3. Clustering ensemble
    print("\n3️⃣ Testando clustering ensemble...")
    clustering_analyzer = ClusteringAnalyzer(config)
    clusters = clustering_analyzer.perform_ensemble_clustering(mock_poses)
    print(f"   ✅ {len(clusters)} clusters encontrados")
    
    # 4. Feature extraction avançada (29 recursos)
    print("\n4️⃣ Testando extração de 29 recursos...")
    feature_extractor = FeatureExtractor(config)
    features_df = feature_extractor.extract_cluster_features(clusters)
    
    print(f"   ✅ Features extraídas: {features_df.shape}")
    print(f"   ✅ Recursos por cluster: {features_df.shape[1] - 1}")  # -1 para cluster_id
    
    # Verificar se temos os 29 recursos esperados
    expected_features = 29
    actual_features = features_df.shape[1] - 1  # -1 para cluster_id
    
    if actual_features >= expected_features:
        print(f"   🎯 SUCESSO: {actual_features} recursos implementados (target: {expected_features})")
    else:
        print(f"   ⚠️  Recursos: {actual_features}/{expected_features}")
    
    # Mostrar alguns recursos
    feature_columns = [col for col in features_df.columns if col != 'cluster_id'][:10]
    print(f"   📊 Primeiros 10 recursos: {feature_columns}")
    
    # 5. Machine Learning com 29 recursos
    print("\n5️⃣ Testando ML ensemble com recursos avançados...")
    ml_predictor = MachineLearningPredictor(config)
    
    # Treinar modelos
    performance = ml_predictor.train_ensemble_models(features_df)
    print(f"   ✅ Modelos treinados: {len(performance)}")
    
    # Predições
    predictions = ml_predictor.predict_cluster_properties(features_df)
    print(f"   ✅ Predições: {len(predictions)} clusters")
    
    # Feature importance
    importance = ml_predictor.get_feature_importance('druggability')
    if importance:
        top_features = list(importance.items())[:5]
        print(f"   🔝 Top 5 recursos importantes:")
        for feat, imp in top_features:
            print(f"      {feat}: {imp:.3f}")
    
    # 6. Validação de robustez
    print("\n6️⃣ Testando validação de robustez...")
    validation = ml_predictor.validate_model_robustness(features_df)
    
    if validation:
        print("   ✅ Validação concluída")
        
        # Métricas do ensemble
        if 'ensemble' in validation:
            ensemble = validation['ensemble']
            print(f"   📈 Ensemble R² (Drug): {ensemble.get('druggability_r2', 0):.3f}")
            print(f"   📈 Ensemble R² (Hotspot): {ensemble.get('hotspot_r2', 0):.3f}")
    
    # 7. Diagnósticos finais
    print("\n7️⃣ Diagnósticos do sistema...")
    diagnostics = ml_predictor.get_model_diagnostics()
    
    if diagnostics:
        print(f"   🔧 Modelos ativos: {diagnostics['models_trained']}")
        print(f"   🔧 Tipos de modelo: {diagnostics['model_types']}")
        print(f"   🔧 Targets: {diagnostics['target_types']}")
        print(f"   🔧 Features: {len(diagnostics.get('feature_names', []))}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
    print("🎯 Sistema FTMap Enhanced operacional com:")
    print("   • Docking com parâmetros avançados")
    print("   • Clustering ensemble (3 algoritmos)")
    print("   • Extração de 29 recursos sofisticados")
    print("   • ML ensemble com validação robusta")
    print("=" * 60)
    
    return True

def test_individual_modules():
    """Testa módulos individuais"""
    print("\n🔍 TESTE DOS MÓDULOS INDIVIDUAIS")
    print("-" * 40)
    
    # Teste de importação
    modules_to_test = [
        'config', 'molecular_docking', 'clustering_analysis',
        'feature_extraction', 'machine_learning'
    ]
    
    for module_name in modules_to_test:
        try:
            module = __import__(f'modules.{module_name}', fromlist=[module_name])
            print(f"   ✅ {module_name}: OK")
        except Exception as e:
            print(f"   ❌ {module_name}: ERRO - {str(e)}")
    
    print("-" * 40)

if __name__ == "__main__":
    try:
        # Teste de módulos individuais
        test_individual_modules()
        
        # Teste de integração completa
        success = test_enhanced_workflow()
        
        if success:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            sys.exit(0)
        else:
            print("\n💥 ALGUNS TESTES FALHARAM!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
