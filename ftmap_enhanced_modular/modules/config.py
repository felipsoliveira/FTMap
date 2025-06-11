#!/usr/bin/env python3
"""
FTMap Enhanced - Config Module
Configurações simplificadas do sistema
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class FTMapConfig:
    """Configurações centralizadas do FTMap Enhanced"""
    
    def __init__(self):
        # Diretórios base
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.input_dir = self.data_dir / "input"
        self.output_dir = self.data_dir / "output"
        self.temp_dir = self.data_dir / "temp"
        
        # Configurações de probe molecules
        self.probe_molecules = [
            'acetone', 'acetaldehyde', 'acetamide', 'acetonitrile',
            'benzaldehyde', 'benzene', 'cyclohexane', 'dimethylether',
            'ethane', 'ethanol', 'formaldehyde', 'formamide',
            'imidazole', 'indole', 'isopropanol', 'methylamine',
            'phenol', 'urea'
        ]
        
        # Configurações de clustering ENSEMBLE (matching original)
        self.clustering_config = {
            'dbscan': {
                'eps': 2.0,
                'min_samples': 3,
                'metric': 'euclidean'
            },
            'hierarchical': {
                'n_clusters': 10,
                'linkage': 'ward',
                'affinity': 'euclidean'
            },
            'agglomerative': {
                'n_clusters': 10,
                'linkage': 'ward',
                'connectivity': None
            },
            'ensemble': {
                'min_cluster_size': 5,
                'consensus_threshold': 0.7,
                'algorithms': ['hierarchical', 'dbscan', 'agglomerative'],
                'weights': [0.4, 0.3, 0.3]  # Hierarchical, DBSCAN, Agglomerative
            }
        }
        
        # Configurações de machine learning
        self.ml_config = {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 5,
                'random_state': 42
            },
            'gradient_boosting': {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6,
                'random_state': 42
            },
            'neural_network': {
                'hidden_layer_sizes': (100, 50),
                'activation': 'relu',
                'solver': 'adam',
                'max_iter': 500,
                'random_state': 42
            },
            'ensemble_weights': [0.4, 0.3, 0.3]  # RF, GB, NN
        }
        
        # Configurações de docking ENHANCED (matching original algorithm)
        self.docking_config = {
            'exhaustiveness': 128,       # 2x enhanced from 64
            'num_modes': 500,           # 2.5x enhanced from 200
            'energy_range': 8.0,        # Expanded from 3.0 to 8.0
            'cpu_count': os.cpu_count() or 4,
            'grid_expansion': 1.5,      # Grid 50% larger
            'rotation_sampling': 4,     # 4x more rotations
            'conformer_variants': 3,    # 3 variants per probe
            'search_space_expansion': 1.5
        }
        
        # Multiple energy cutoffs for comprehensive sampling
        self.energy_cutoffs = {
            'high_affinity': -8.0,      # Excellent poses
            'good_affinity': -6.0,      # Good poses  
            'moderate_affinity': -4.0,   # Moderate poses
            'weak_affinity': -2.0       # Weak poses (exploratory)
        }
        
        # Limiares de análise ENHANCED
        self.analysis_thresholds = {
            'druggability_cutoff': 0.7,
            'hotspot_cutoff': 16.0,
            'energy_cutoff': -1.0,
            'cluster_size_min': 3,
            'target_poses': 100000,      # Target 100k+ poses vs E-FTMap's 80k
            'target_clusters': 180,      # Enhanced clustering
            'target_features': 29        # vs E-FTMap's 15 features
        }
        
        # Configurações de visualização
        self.color_scheme = 'viridis'
        self.visualization_config = {
            'figure_size': (12, 8),
            'dpi': 300,
            'format': 'png',
            'style': 'seaborn'
        }
        
    def get_probe_library_path(self) -> Path:
        """Retorna o caminho para a biblioteca de probes"""
        return self.data_dir / "probe_library"
    
    def get_tools_config(self) -> Dict[str, str]:
        """Configurações de ferramentas externas"""
        return {
            'vina_executable': 'vina',
            'babel_executable': 'obabel',
            'fpocket_executable': 'fpocket',
            'castp_executable': 'castp'
        }
    
    def ensure_directories(self):
        """Cria diretórios necessários se não existirem"""
        for directory in [self.input_dir, self.output_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

# Re-exportar para uso nos módulos
__all__ = ['FTMapConfig']
