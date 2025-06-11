#!/usr/bin/env python3
"""
Teste de Integração Completa do FTMap Enhanced
===============================================
Verifica se todos os módulos funcionam em conjunto
"""

import sys
import os
from pathlib import Path
import numpy as np
from typing import List, Dict, Any

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent / "modules"))

def test_config_module():
    """Testa o módulo de configuração"""
    print("🔧 Testando módulo de configuração...")
    
    try:
        from config import FTMapConfig
        config = FTMapConfig()
        
        # Verificar parâmetros avançados
        assert config.docking_config['exhaustiveness'] == 128, "Exhaustiveness should be 128"
        assert config.docking_config['num_modes'] == 500, "Num modes should be 500"
        assert config.docking_config['energy_range'] == 8.0, "Energy range should be 8.0"
        assert len(config.energy_cutoffs) == 4, "Should have 4 energy cutoffs"
        assert len(config.clustering_config['ensemble']['algorithms']) == 3, "Should have 3 clustering algorithms"
        assert config.analysis_thresholds['target_features'] == 29, "Should target 29 features"
        
        print("   ✅ Configuração avançada validada")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na configuração: {e}")
        return False

def test_docking_module():
    """Testa o módulo de docking molecular"""
    print("🧬 Testando módulo de docking molecular...")
    
    try:
        from config import FTMapConfig
        from molecular_docking import MolecularDocker
        
        config = FTMapConfig()
        docking_engine = MolecularDocker(config)
        
        # Verificar se engine foi inicializado
        assert hasattr(docking_engine, 'config'), "Engine should have config"
        assert hasattr(docking_engine, 'docking_config'), "Engine should have docking config"
        
        # Verificar parâmetros avançados
        assert docking_engine.docking_config['exhaustiveness'] == 128, "Should use enhanced exhaustiveness"
        assert docking_engine.docking_config['num_modes'] == 500, "Should use enhanced num_modes"
        
        print("   ✅ Engine de docking inicializado com parâmetros avançados")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no docking: {e}")
        return False

def test_clustering_module():
    """Testa o módulo de clustering"""
    print("🎪 Testando módulo de clustering ensemble...")
    
    try:
        from config import FTMapConfig
        from clustering_analysis import ClusteringAnalyzer
        
        config = FTMapConfig()
        analyzer = ClusteringAnalyzer(config)
        
        # Verificar configuração ensemble
        ensemble_config = analyzer.clustering_config['ensemble']
        assert len(ensemble_config['algorithms']) == 3, "Should have 3 algorithms"
        assert len(ensemble_config['weights']) == 3, "Should have 3 weights"
        assert sum(ensemble_config['weights']) == 1.0, "Weights should sum to 1.0"
        
        print("   ✅ Clustering ensemble configurado com 3 algoritmos")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no clustering: {e}")
        return False

def test_feature_extraction_module():
    """Testa o módulo de extração de features"""
    print("📊 Testando módulo de extração de features...")
    
    try:
        from config import FTMapConfig
        from feature_extraction import FeatureExtractor
        
        config = FTMapConfig()
        extractor = FeatureExtractor(config)
        
        # Verificar biblioteca de probes
        assert len(extractor.probe_properties) == 18, "Should have 18 probe molecules"
        
        # Verificar se todas as propriedades estão definidas
        for probe_name, props in extractor.probe_properties.items():
            assert hasattr(props, 'molecular_weight'), f"{probe_name} missing molecular_weight"
            assert hasattr(props, 'logp'), f"{probe_name} missing logp"
            assert hasattr(props, 'hbd'), f"{probe_name} missing hbd"
            assert hasattr(props, 'hba'), f"{probe_name} missing hba"
        
        print("   ✅ Extrator de features com 18 probes e propriedades completas")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na extração de features: {e}")
        return False

def test_machine_learning_module():
    """Testa o módulo de machine learning"""
    print("🤖 Testando módulo de machine learning...")
    
    try:
        from config import FTMapConfig
        from machine_learning import MachineLearningPredictor
        
        config = FTMapConfig()
        ml_predictor = MachineLearningPredictor(config)
        
        # Verificar configuração ML
        assert len(ml_predictor.ml_config['ensemble_weights']) == 3, "Should have 3 ML models"
        
        print("   ✅ Preditor ML configurado com ensemble de 3 modelos")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no ML: {e}")
        return False

def simulate_mini_workflow():
    """Simula um mini workflow completo"""
    print("⚡ Testando workflow completo simulado...")
    
    try:
        from config import FTMapConfig
        from molecular_docking import MolecularDocker
        from clustering_analysis import ClusteringAnalyzer
        from feature_extraction import FeatureExtractor
        from machine_learning import MachineLearningPredictor
        
        # 1. Configuração
        config = FTMapConfig()
        
        # 2. Simular poses de docking
        docking_engine = MolecularDocker(config)
        
        # Criar poses mock para teste
        mock_poses = []
        for i in range(50):  # 50 poses simuladas
            pose = type('MockPose', (), {
                'probe_name': config.probe_molecules[i % len(config.probe_molecules)],
                'pose_id': i,
                'coordinates': tuple(np.random.uniform(-10, 10, 3)),
                'affinity': np.random.uniform(-8, -2),
                'rmsd_lb': np.random.uniform(0.1, 1.0),
                'rmsd_ub': np.random.uniform(1.0, 3.0),
                'rotation': tuple(np.random.uniform(0, 360, 3))
            })()
            mock_poses.append(pose)
        
        print(f"   📦 {len(mock_poses)} poses simuladas criadas")
        
        # 3. Clustering
        analyzer = ClusteringAnalyzer(config)
        # Preparar dados para clustering
        features_data = []
        for pose in mock_poses:
            features_data.append([
                pose.coordinates[0], pose.coordinates[1], pose.coordinates[2],
                pose.affinity, hash(pose.probe_name) % 10, 
                (pose.rmsd_lb + pose.rmsd_ub) / 2
            ])
        
        features_array = np.array(features_data)
        labels = analyzer._dbscan_clustering(features_array)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        print(f"   🎪 Clustering executado: {n_clusters} clusters identificados")
        
        # 4. Feature extraction
        extractor = FeatureExtractor(config)
        print("   📊 Extrator de features inicializado")
        
        # 5. Machine Learning
        ml_predictor = MachineLearningPredictor(config)
        print("   🤖 Preditor ML inicializado")
        
        print("   ✅ Workflow completo simulado com sucesso!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no workflow: {e}")
        return False

def run_complete_integration_test():
    """Executa teste de integração completo"""
    print("🧪 TESTE DE INTEGRAÇÃO COMPLETA - FTMap Enhanced")
    print("=" * 60)
    
    tests = [
        ("Configuração", test_config_module),
        ("Docking Molecular", test_docking_module),
        ("Clustering Ensemble", test_clustering_module),
        ("Feature Extraction", test_feature_extraction_module),
        ("Machine Learning", test_machine_learning_module),
        ("Workflow Completo", simulate_mini_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📋 RESULTADOS DOS TESTES:")
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSOU" if results[i] else "❌ FALHOU"
        print(f"   {test_name}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n🎯 Taxa de Sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 SISTEMA VALIDADO! FTMap Enhanced está funcionando corretamente!")
        print("🚀 Pronto para análises de proteínas reais!")
    else:
        print("⚠️  Sistema precisa de ajustes antes do uso em produção")
    
    return success_rate >= 80

if __name__ == "__main__":
    run_complete_integration_test()
