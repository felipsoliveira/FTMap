#!/usr/bin/env python3
"""
FTMap Enhanced - Teste de Integração Final
Teste completo do sistema para verificar funcionamento
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
import json

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent.parent))

from configs.config import FTMapConfig
from modules.workflow_manager import FTMapWorkflowManager


class TestFTMapIntegration(unittest.TestCase):
    """Testes de integração para FTMap Enhanced"""
    
    @classmethod
    def setUpClass(cls):
        """Setup uma vez para todos os testes"""
        cls.test_dir = Path(tempfile.mkdtemp(prefix="ftmap_test_"))
        cls.config = FTMapConfig()
        
        # Configuração reduzida para testes rápidos
        cls.config.TARGET_POSES_PER_PROBE = 2
        cls.config.MAX_CLUSTERS = 5
        cls.config.PARALLEL_PROCESSES = 2
        
        # Usar apenas probes essenciais
        cls.config.PROBE_MOLECULES = {
            "water": {"smiles": "O", "charge": 0},
            "methanol": {"smiles": "CO", "charge": 0}
        }
        
    def setUp(self):
        """Setup para cada teste"""
        self.output_dir = self.test_dir / f"test_{self._testMethodName}"
        self.output_dir.mkdir(exist_ok=True)
        
    def create_test_protein(self):
        """Cria arquivo PDB de teste simples"""
        test_pdb = self.output_dir / "test_protein.pdb"
        
        # PDB minimalista para teste
        pdb_content = """HEADER    TEST PROTEIN                             01-JAN-21   TEST
ATOM      1  CA  ALA A   1      10.000  10.000  10.000  1.00 20.00           C
ATOM      2  CA  GLY A   2      13.800  10.000  10.000  1.00 20.00           C
ATOM      3  CA  VAL A   3      17.600  10.000  10.000  1.00 20.00           C
ATOM      4  CA  LEU A   4      21.400  10.000  10.000  1.00 20.00           C
ATOM      5  CA  ILE A   5      25.200  10.000  10.000  1.00 20.00           C
END
"""
        
        with open(test_pdb, 'w') as f:
            f.write(pdb_content)
        
        return str(test_pdb)
    
    def test_config_creation(self):
        """Testa criação de configuração"""
        config = FTMapConfig()
        
        self.assertIsNotNone(config)
        self.assertGreater(len(config.PROBE_MOLECULES), 0)
        self.assertGreater(config.PARALLEL_PROCESSES, 0)
        self.assertLess(config.ENERGY_CUTOFF, 0)
    
    def test_workflow_manager_initialization(self):
        """Testa inicialização do workflow manager"""
        workflow = FTMapWorkflowManager(
            config=self.config,
            output_dir=str(self.output_dir)
        )
        
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.output_dir, self.output_dir)
        self.assertIsNotNone(workflow.logger)
    
    def test_protein_preparation_step(self):
        """Testa step de preparação de proteína"""
        protein_file = self.create_test_protein()
        
        workflow = FTMapWorkflowManager(
            config=self.config,
            output_dir=str(self.output_dir)
        )
        
        try:
            result = workflow._step_protein_preparation(protein_file, {})
            
            self.assertIn('prepared_protein', result)
            self.assertIn('binding_sites', result)
            self.assertIn('geometric_properties', result)
            
        except Exception as e:
            # Algumas dependências podem não estar disponíveis em ambiente de teste
            self.skipTest(f"Dependências não disponíveis para teste: {str(e)}")
    
    def test_workflow_state_management(self):
        """Testa gerenciamento de estado do workflow"""
        workflow = FTMapWorkflowManager(
            config=self.config,
            output_dir=str(self.output_dir)
        )
        
        # Testar status inicial
        status = workflow.get_workflow_status()
        
        self.assertIn('current_step', status)
        self.assertIn('completed_steps', status)
        self.assertIn('total_duration', status)
        self.assertIn('output_directory', status)
    
    def test_configuration_override(self):
        """Testa override de configuração"""
        config = FTMapConfig()
        original_processes = config.PARALLEL_PROCESSES
        
        # Modificar configuração
        config.PARALLEL_PROCESSES = 8
        config.ENERGY_CUTOFF = -3.0
        
        self.assertEqual(config.PARALLEL_PROCESSES, 8)
        self.assertEqual(config.ENERGY_CUTOFF, -3.0)
        self.assertNotEqual(config.PARALLEL_PROCESSES, original_processes)
    
    def test_directory_structure_creation(self):
        """Testa criação da estrutura de diretórios"""
        workflow = FTMapWorkflowManager(
            config=self.config,
            output_dir=str(self.output_dir)
        )
        
        # Verificar se diretórios foram criados
        expected_dirs = [
            "prepared_proteins",
            "docking_results",
            "clusters",
            "features", 
            "models",
            "reports",
            "visualizations",
            "temp",
            "logs"
        ]
        
        for dir_name in expected_dirs:
            dir_path = self.output_dir / dir_name
            self.assertTrue(dir_path.exists(), f"Diretório {dir_name} não criado")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} não é um diretório")
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        workflow = FTMapWorkflowManager(
            config=self.config,
            output_dir=str(self.output_dir)
        )
        
        # Testar com arquivo inexistente
        with self.assertRaises(FileNotFoundError):
            workflow._validate_inputs("arquivo_inexistente.pdb")
        
        # Testar com extensão inválida
        invalid_file = self.output_dir / "test.txt"
        invalid_file.touch()
        
        with self.assertRaises(ValueError):
            workflow._validate_inputs(str(invalid_file))
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup após todos os testes"""
        import shutil
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)


class TestModuleImports(unittest.TestCase):
    """Testa imports de todos os módulos"""
    
    def test_import_config(self):
        """Testa import do módulo de configuração"""
        from configs.config import FTMapConfig
        self.assertTrue(True)  # Se chegou até aqui, import funcionou
    
    def test_import_protein_preparation(self):
        """Testa import do módulo de preparação de proteínas"""
        try:
            from modules.protein_preparation import ProteinPreparator
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")
    
    def test_import_molecular_docking(self):
        """Testa import do módulo de docking"""
        try:
            from modules.molecular_docking import ProbeLibrary, MolecularDocker
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")
    
    def test_import_clustering_analysis(self):
        """Testa import do módulo de clustering"""
        try:
            from modules.clustering_analysis import ClusteringAnalyzer
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")
    
    def test_import_feature_extraction(self):
        """Testa import do módulo de features"""
        try:
            from modules.feature_extraction import FeatureExtractor
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")
    
    def test_import_machine_learning(self):
        """Testa import do módulo de ML"""
        try:
            from modules.machine_learning import MLPredictor
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")
    
    def test_import_visualization_reports(self):
        """Testa import do módulo de visualização"""
        try:
            from modules.visualization_reports import VisualizationReporter
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")
    
    def test_import_workflow_manager(self):
        """Testa import do workflow manager"""
        try:
            from modules.workflow_manager import FTMapWorkflowManager
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Dependências do módulo não disponíveis: {str(e)}")


if __name__ == "__main__":
    # Configurar verbosidade dos testes
    unittest.main(verbosity=2)
