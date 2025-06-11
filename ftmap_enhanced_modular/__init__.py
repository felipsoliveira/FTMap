#!/usr/bin/env python3
"""
FTMap Enhanced - Arquivo __init__.py do módulo principal
"""

__version__ = "2.0.0"
__author__ = "FTMap Enhanced Team"
__email__ = "support@ftmap-enhanced.org"
__description__ = "Sistema Modular de Análise de Druggability"

# Imports principais para facilitar uso
from .configs.config import FTMapConfig
from .modules.workflow_manager import FTMapWorkflowManager

# Metadata do pacote
__all__ = [
    'FTMapConfig',
    'FTMapWorkflowManager',
    '__version__',
    '__author__',
    '__description__'
]

def get_version():
    """Retorna versão do FTMap Enhanced"""
    return __version__

def get_info():
    """Retorna informações do pacote"""
    return {
        'name': 'FTMap Enhanced',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules': [
            'protein_preparation',
            'molecular_docking', 
            'clustering_analysis',
            'feature_extraction',
            'machine_learning',
            'visualization_reports',
            'workflow_manager'
        ]
    }
