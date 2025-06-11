"""
Módulo de Preparação de Proteínas
================================
Responsável por análise, preparação e validação de estruturas proteicas.
"""

import os
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from config import FTMapConfig

@dataclass
class ProteinInfo:
    """Informações extraídas da proteína"""
    pdb_id: str
    num_residues: int
    num_atoms: int
    molecular_weight: float
    center_of_mass: Tuple[float, float, float]
    binding_sites: List[Dict]
    cavity_volume: float
    surface_area: float

class ProteinPreparator:
    """Classe responsável pela preparação de proteínas"""
    
    def __init__(self, config: Optional[FTMapConfig] = None):
        self.config = config or FTMapConfig()
        self.temp_dir = self.config.temp_dir
        self.output_dir = self.config.output_dir
        
    def prepare_protein(self, pdb_file: str, protein_id: str) -> ProteinInfo:
        """
        Prepara e analisa a estrutura proteica
        
        Args:
            pdb_file: Caminho para o arquivo PDB
            protein_id: Identificador da proteína
            
        Returns:
            ProteinInfo: Informações estruturais da proteína
        """
        print(f"📋 Preparando proteína: {protein_id}")
        
        # Validar arquivo PDB
        if not Path(pdb_file).exists():
            raise FileNotFoundError(f"Arquivo PDB não encontrado: {pdb_file}")
        
        # Extrair informações básicas
        protein_info = self._extract_protein_info(pdb_file, protein_id)
        
        # Limpar e otimizar estrutura
        cleaned_pdb = self._clean_protein_structure(pdb_file, protein_id)
        
        # Detectar sítios de ligação
        binding_sites = self._detect_binding_sites(cleaned_pdb, protein_id)
        protein_info.binding_sites = binding_sites
        
        # Calcular propriedades geométricas
        self._calculate_geometric_properties(protein_info, cleaned_pdb)
        
        print(f"✅ Proteína {protein_id} preparada com sucesso!")
        print(f"   - Resíduos: {protein_info.num_residues}")
        print(f"   - Átomos: {protein_info.num_atoms}")
        print(f"   - Sítios de ligação encontrados: {len(binding_sites)}")
        
        return protein_info
    
    def _extract_protein_info(self, pdb_file: str, protein_id: str) -> ProteinInfo:
        """Extrai informações básicas da estrutura PDB"""
        coordinates = []
        residues = set()
        atom_count = 0
        
        with open(pdb_file, 'r') as f:
            for line in f:
                if line.startswith(('ATOM', 'HETATM')):
                    atom_count += 1
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coordinates.append([x, y, z])
                    
                    # Extrair informação do resíduo
                    res_name = line[17:20].strip()
                    res_num = line[22:26].strip()
                    chain = line[21].strip()
                    residues.add(f"{chain}_{res_name}_{res_num}")
        
        coordinates = np.array(coordinates)
        center_of_mass = tuple(np.mean(coordinates, axis=0))
        
        return ProteinInfo(
            pdb_id=protein_id,
            num_residues=len(residues),
            num_atoms=atom_count,
            molecular_weight=atom_count * 12.0,  # Aproximação
            center_of_mass=center_of_mass,
            binding_sites=[],
            cavity_volume=0.0,
            surface_area=0.0
        )
    
    def _clean_protein_structure(self, pdb_file: str, protein_id: str) -> str:
        """Limpa e otimiza a estrutura proteica"""
        cleaned_file = self.temp_dir / f"{protein_id}_cleaned.pdb"
        
        # Remover águas e heteroátomos desnecessários
        with open(pdb_file, 'r') as input_f, open(cleaned_file, 'w') as output_f:
            for line in input_f:
                if line.startswith('ATOM'):
                    output_f.write(line)
                elif line.startswith('HETATM') and 'HOH' not in line:
                    # Manter heteroátomos que não sejam água
                    output_f.write(line)
        
        return str(cleaned_file)
    
    def _detect_binding_sites(self, pdb_file: str, protein_id: str) -> List[Dict]:
        """Detecta sítios de ligação usando fpocket ou métodos alternativos"""
        binding_sites = []
        
        try:
            # Tentar usar fpocket se disponível
            fpocket_cmd = [
                self.config.get_tools_config()['fpocket_executable'],
                '-f', pdb_file
            ]
            
            result = subprocess.run(
                fpocket_cmd, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if result.returncode == 0:
                binding_sites = self._parse_fpocket_output(protein_id)
            else:
                print("⚠️  fpocket não disponível, usando detecção geométrica")
                binding_sites = self._geometric_cavity_detection(pdb_file)
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️  fpocket não encontrado, usando detecção geométrica")
            binding_sites = self._geometric_cavity_detection(pdb_file)
        
        return binding_sites
    
    def _geometric_cavity_detection(self, pdb_file: str) -> List[Dict]:
        """Detecção geométrica simples de cavidades"""
        coordinates = []
        
        with open(pdb_file, 'r') as f:
            for line in f:
                if line.startswith('ATOM'):
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coordinates.append([x, y, z])
        
        coords = np.array(coordinates)
        center = np.mean(coords, axis=0)
        
        # Cavidade simples baseada no centro geométrico
        return [{
            'id': 1,
            'center': tuple(center),
            'volume': 100.0,  # Valor padrão
            'score': 0.5,
            'atoms': len(coordinates)
        }]
    
    def _parse_fpocket_output(self, protein_id: str) -> List[Dict]:
        """Parse da saída do fpocket"""
        # Implementação simplificada
        return [{
            'id': 1,
            'center': (0.0, 0.0, 0.0),
            'volume': 100.0,
            'score': 0.8,
            'atoms': 50
        }]
    
    def _calculate_geometric_properties(self, protein_info: ProteinInfo, pdb_file: str):
        """Calcula propriedades geométricas adicionais"""
        # Simplificado - em implementação real usaria bibliotecas como PyMOL
        protein_info.cavity_volume = 150.0
        protein_info.surface_area = 1000.0
