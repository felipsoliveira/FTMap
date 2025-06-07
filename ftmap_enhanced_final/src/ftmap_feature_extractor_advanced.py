#!/usr/bin/env python3
"""
FTMap Advanced Feature Extractor - Sistema de 25+ Features
Extração de características avançadas para competir com E-FTMap
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.spatial.distance import cdist, pdist
from scipy.spatial import ConvexHull, distance_matrix
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProbeProperties:
    """Propriedades químicas dos probes"""
    molecular_weight: float
    logp: float  # Coeficiente de partição
    hbd: int     # Hydrogen bond donors
    hba: int     # Hydrogen bond acceptors
    psa: float   # Polar surface area
    dipole: float # Momento dipolar
    aromatic: bool
    polar: bool
    charged: bool

class FTMapAdvancedFeatureExtractor:
    """Extrator de features avançadas para poses FTMap"""
    
    def __init__(self):
        self.probe_properties = self._initialize_probe_properties()
        self.protein_coords = None
        self.protein_surface = None
        self.cavity_info = None
        
    def _initialize_probe_properties(self) -> Dict[str, ProbeProperties]:
        """Inicializa propriedades químicas dos 18 probes"""
        return {
            'ethanol': ProbeProperties(46.07, -0.31, 1, 1, 20.23, 1.69, False, True, False),
            'isopropanol': ProbeProperties(60.10, 0.05, 1, 1, 20.23, 1.66, False, True, False),
            'acetone': ProbeProperties(58.08, -0.24, 0, 1, 17.07, 2.88, False, True, False),
            'benzene': ProbeProperties(78.11, 2.13, 0, 0, 0.0, 0.0, True, False, False),
            'phenol': ProbeProperties(94.11, 1.46, 1, 1, 20.23, 1.45, True, True, False),
            'imidazole': ProbeProperties(68.08, -0.76, 1, 2, 28.68, 3.61, True, True, True),
            'indole': ProbeProperties(117.15, 2.14, 1, 1, 15.79, 2.11, True, True, False),
            'urea': ProbeProperties(60.06, -2.11, 2, 1, 69.11, 4.56, False, True, False),
            'acetamide': ProbeProperties(59.07, -1.26, 1, 1, 43.09, 3.76, False, True, False),
            'water': ProbeProperties(18.02, -1.38, 2, 1, 0.0, 1.85, False, True, False),
            'methylamine': ProbeProperties(31.06, -0.57, 2, 1, 26.02, 1.31, False, True, True),
            'cyclohexane': ProbeProperties(84.16, 3.44, 0, 0, 0.0, 0.0, False, False, False),
            'ethane': ProbeProperties(30.07, 1.81, 0, 0, 0.0, 0.0, False, False, False),
            'acetaldehyde': ProbeProperties(44.05, 0.45, 0, 1, 17.07, 2.75, False, True, False),
            'dmf': ProbeProperties(73.09, -1.01, 0, 1, 20.31, 3.82, False, True, False),
            'dimethylether': ProbeProperties(46.07, 0.10, 0, 1, 9.23, 1.30, False, True, False),
            'acetonitrile': ProbeProperties(41.05, -0.34, 0, 1, 23.79, 3.92, False, True, False),
            'benzaldehyde': ProbeProperties(106.12, 1.48, 0, 1, 17.07, 3.0, True, True, False)
        }
    
    def extract_chemical_features(self, pose_data: Dict) -> Dict[str, float]:
        """Extrai 8 features químicas do probe"""
        probe_name = pose_data['probe']
        props = self.probe_properties.get(probe_name)
        
        if not props:
            logger.warning(f"Propriedades não encontradas para probe: {probe_name}")
            return {f'chem_{i}': 0.0 for i in range(8)}
        
        return {
            'chem_molecular_weight': props.molecular_weight,
            'chem_logp': props.logp,
            'chem_hbd': float(props.hbd),
            'chem_hba': float(props.hba),
            'chem_psa': props.psa,
            'chem_dipole': props.dipole,
            'chem_aromatic': float(props.aromatic),
            'chem_polar': float(props.polar)
        }
    
    def extract_spatial_features(self, pose_data: Dict, protein_coords: np.ndarray) -> Dict[str, float]:
        """Extrai 7 features espaciais da pose"""
        coords = np.array(pose_data['coordinates'])
        
        # Centroide da proteína
        protein_centroid = np.mean(protein_coords, axis=0)
        
        # Distâncias
        dist_to_centroid = np.linalg.norm(coords - protein_centroid)
        
        # Distância à superfície (aproximação)
        distances_to_atoms = cdist([coords], protein_coords)[0]
        dist_to_surface = np.min(distances_to_atoms)
        
        # Profundidade de cavidade (baseada em vizinhança)
        nearby_atoms = distances_to_atoms < 8.0  # 8Å de raio
        cavity_depth = np.sum(nearby_atoms) / len(distances_to_atoms)
        
        # Acessibilidade ao solvente (aproximação geométrica)
        solvent_accessible = self._calculate_solvent_accessibility(coords, protein_coords)
        
        # Curvatura local (baseada na distribuição de átomos próximos)
        local_curvature = self._calculate_local_curvature(coords, protein_coords)
        
        # Volume de cavidade local
        local_volume = self._calculate_local_cavity_volume(coords, protein_coords)
        
        return {
            'spatial_x': coords[0],
            'spatial_y': coords[1], 
            'spatial_z': coords[2],
            'spatial_dist_centroid': dist_to_centroid,
            'spatial_dist_surface': dist_to_surface,
            'spatial_cavity_depth': cavity_depth,
            'spatial_solvent_accessible': solvent_accessible,
            'spatial_local_curvature': local_curvature,
            'spatial_local_volume': local_volume
        }
    
    def extract_interaction_features(self, pose_data: Dict, protein_coords: np.ndarray) -> Dict[str, float]:
        """Extrai 6 features de interação proteína-probe"""
        coords = np.array(pose_data['coordinates'])
        energy = pose_data['energy']
        
        # Número de contatos próximos
        distances = cdist([coords], protein_coords)[0]
        close_contacts = np.sum(distances < 4.0)  # Contatos < 4Å
        medium_contacts = np.sum((distances >= 4.0) & (distances < 6.0))  # 4-6Å
        
        # Energia Van der Waals (aproximação baseada na distância)
        vdw_energy = self._calculate_vdw_energy(coords, protein_coords, pose_data['probe'])
        
        # Energia eletrostática (aproximação)
        electrostatic_energy = self._calculate_electrostatic_energy(coords, protein_coords, pose_data['probe'])
        
        # Potencial H-bond
        hbond_potential = self._calculate_hbond_potential(coords, protein_coords, pose_data['probe'])
        
        # Complementaridade de forma
        shape_complementarity = self._calculate_shape_complementarity(coords, protein_coords)
        
        return {
            'interact_close_contacts': float(close_contacts),
            'interact_medium_contacts': float(medium_contacts),
            'interact_vdw_energy': vdw_energy,
            'interact_electrostatic': electrostatic_energy,
            'interact_hbond_potential': hbond_potential,
            'interact_shape_complement': shape_complementarity
        }
    
    def extract_consensus_features(self, pose_data: Dict, all_poses: List[Dict], 
                                 neighborhood_radius: float = 3.0) -> Dict[str, float]:
        """Extrai 4 features de consenso baseadas em outras poses"""
        coords = np.array(pose_data['coordinates'])
        
        # Coletar coordenadas de todas as poses
        all_coords = np.array([p['coordinates'] for p in all_poses])
        
        # Densidade de consenso local
        distances = cdist([coords], all_coords)[0]
        nearby_poses = np.sum(distances < neighborhood_radius)
        consensus_density = nearby_poses / len(all_poses)
        
        # Número de probes diferentes na vizinhança
        nearby_indices = np.where(distances < neighborhood_radius)[0]
        nearby_probes = set(all_poses[i]['probe'] for i in nearby_indices)
        num_different_probes = len(nearby_probes)
        
        # Score de concordância (baseado em energias similares)
        nearby_energies = [all_poses[i]['energy'] for i in nearby_indices]
        if nearby_energies:
            energy_std = np.std(nearby_energies)
            concordance_score = 1.0 / (1.0 + energy_std)  # Alta concordância = baixo desvio
        else:
            concordance_score = 0.0
        
        # Ranking energético local
        better_poses_nearby = sum(1 for i in nearby_indices 
                                 if all_poses[i]['energy'] < pose_data['energy'])
        local_energy_rank = better_poses_nearby / max(1, nearby_poses)
        
        return {
            'consensus_density': consensus_density,
            'consensus_num_probes': float(num_different_probes),
            'consensus_concordance': concordance_score,
            'consensus_energy_rank': local_energy_rank
        }
    
    def _calculate_solvent_accessibility(self, coords: np.ndarray, protein_coords: np.ndarray) -> float:
        """Calcula acessibilidade ao solvente (aproximação)"""
        # Contar átomos numa esfera de 5Å
        distances = cdist([coords], protein_coords)[0]
        atoms_in_sphere = np.sum(distances < 5.0)
        
        # Normalizar (máximo teórico de ~100 átomos numa esfera de 5Å)
        accessibility = max(0.0, (100 - atoms_in_sphere) / 100.0)
        return accessibility
    
    def _calculate_local_curvature(self, coords: np.ndarray, protein_coords: np.ndarray) -> float:
        """Calcula curvatura local baseada na distribuição de átomos"""
        distances = cdist([coords], protein_coords)[0]
        nearby_atoms = protein_coords[distances < 6.0]
        
        if len(nearby_atoms) < 4:
            return 0.0
        
        try:
            # Usar convex hull como aproximação de curvatura
            hull = ConvexHull(nearby_atoms)
            volume = hull.volume
            surface_area = hull.area
            
            # Razão volume/área como medida de curvatura
            curvature = volume / surface_area if surface_area > 0 else 0.0
            return min(curvature, 10.0)  # Limitar valor máximo
        except:
            return 0.0
    
    def _calculate_local_cavity_volume(self, coords: np.ndarray, protein_coords: np.ndarray) -> float:
        """Calcula volume da cavidade local"""
        distances = cdist([coords], protein_coords)[0]
        
        # Volume baseado na densidade de átomos próximos
        sphere_volumes = {3.0: 113.1, 4.0: 268.1, 5.0: 523.6, 6.0: 904.8}  # Volume de esferas
        
        volume_estimate = 0.0
        for radius, sphere_vol in sphere_volumes.items():
            atoms_in_sphere = np.sum(distances < radius)
            occupied_volume = atoms_in_sphere * 20.0  # ~20 Ų por átomo
            free_volume = max(0.0, sphere_vol - occupied_volume)
            volume_estimate = max(volume_estimate, free_volume)
        
        return volume_estimate
    
    def _calculate_vdw_energy(self, coords: np.ndarray, protein_coords: np.ndarray, probe: str) -> float:
        """Calcula energia Van der Waals aproximada"""
        distances = cdist([coords], protein_coords)[0]
        
        # Parâmetros Lennard-Jones aproximados
        probe_props = self.probe_properties.get(probe)
        if not probe_props:
            return 0.0
        
        # Energia VdW = sum(A/r^12 - B/r^6) para distâncias próximas
        vdw_energy = 0.0
        for dist in distances:
            if 2.0 < dist < 8.0:  # Range relevante
                r6 = dist ** 6
                r12 = r6 ** 2
                # Parâmetros simplificados baseados no probe
                A = probe_props.molecular_weight * 0.1
                B = A * 2.0
                vdw_energy += (A / r12) - (B / r6)
        
        return min(max(vdw_energy, -50.0), 50.0)  # Limitar valores extremos
    
    def _calculate_electrostatic_energy(self, coords: np.ndarray, protein_coords: np.ndarray, probe: str) -> float:
        """Calcula energia eletrostática aproximada"""
        probe_props = self.probe_properties.get(probe)
        if not probe_props or not probe_props.polar:
            return 0.0
        
        distances = cdist([coords], protein_coords)[0]
        
        # Energia eletrostática simplificada baseada em dipolo
        electrostatic = 0.0
        for dist in distances:
            if dist < 6.0:  # Range relevante
                # E = q1*q2/(4πε*r)
                charge_interaction = probe_props.dipole / (dist ** 2)
                electrostatic += charge_interaction
        
        return min(max(electrostatic, -20.0), 20.0)  # Limitar valores extremos
    
    def _calculate_hbond_potential(self, coords: np.ndarray, protein_coords: np.ndarray, probe: str) -> float:
        """Calcula potencial de ligação de hidrogênio"""
        probe_props = self.probe_properties.get(probe)
        if not probe_props:
            return 0.0
        
        # Apenas probes com capacidade de H-bond
        if probe_props.hbd == 0 and probe_props.hba == 0:
            return 0.0
        
        distances = cdist([coords], protein_coords)[0]
        
        # Potencial H-bond baseado na distância e capacidade do probe
        hbond_potential = 0.0
        hbond_capacity = probe_props.hbd + probe_props.hba
        
        for dist in distances:
            if 2.5 < dist < 3.5:  # Range ideal para H-bonds
                potential = hbond_capacity * (1.0 / dist) * np.exp(-((dist - 3.0) ** 2) / 0.5)
                hbond_potential += potential
        
        return min(hbond_potential, 10.0)  # Limitar valor máximo
    
    def _calculate_shape_complementarity(self, coords: np.ndarray, protein_coords: np.ndarray) -> float:
        """Calcula complementaridade de forma"""
        distances = cdist([coords], protein_coords)[0]
        nearby_atoms = protein_coords[distances < 5.0]
        
        if len(nearby_atoms) < 3:
            return 0.0
        
        # Calcular "encaixe" baseado na distribuição espacial
        # Medida de quão bem o probe se encaixa na cavidade
        
        # Variância das distâncias como medida de complementaridade
        distance_variance = np.var(distances[distances < 5.0])
        
        # Complementaridade = baixa variância (encaixe uniforme)
        complementarity = 1.0 / (1.0 + distance_variance)
        
        return min(complementarity, 1.0)
    
    def extract_all_features(self, pose_data: Dict, all_poses: List[Dict], 
                           protein_coords: np.ndarray) -> Dict[str, float]:
        """Extrai todas as 25+ features de uma pose"""
        
        # Extrair cada categoria de features
        chemical_features = self.extract_chemical_features(pose_data)
        spatial_features = self.extract_spatial_features(pose_data, protein_coords)
        interaction_features = self.extract_interaction_features(pose_data, protein_coords)
        consensus_features = self.extract_consensus_features(pose_data, all_poses)
        
        # Features básicas existentes
        basic_features = {
            'basic_energy': pose_data['energy'],
            'basic_probe_id': hash(pose_data['probe']) % 1000,  # ID numérico do probe
        }
        
        # Combinar todas as features
        all_features = {}
        all_features.update(basic_features)
        all_features.update(chemical_features)
        all_features.update(spatial_features)
        all_features.update(interaction_features)
        all_features.update(consensus_features)
        
        return all_features
    
    def process_all_poses(self, poses_file: str, protein_coords: np.ndarray, 
                         output_file: str = None) -> pd.DataFrame:
        """Processa todas as poses e extrai features"""
        
        logger.info("🧬 Iniciando extração de features avançadas...")
        
        # Carregar poses
        with open(poses_file, 'r') as f:
            poses_data = json.load(f)
        
        all_poses = poses_data.get('poses', [])
        logger.info(f"   📊 {len(all_poses)} poses carregadas")
        
        # Extrair features para cada pose
        features_list = []
        
        for i, pose in enumerate(all_poses):
            try:
                features = self.extract_all_features(pose, all_poses, protein_coords)
                features['pose_id'] = i
                features_list.append(features)
                
                if (i + 1) % 1000 == 0:
                    logger.info(f"   🔄 Processadas {i + 1}/{len(all_poses)} poses")
                    
            except Exception as e:
                logger.error(f"Erro ao processar pose {i}: {e}")
                continue
        
        # Criar DataFrame
        features_df = pd.DataFrame(features_list)
        
        logger.info(f"✅ Extração concluída!")
        logger.info(f"   📈 {len(features_df)} poses processadas")
        logger.info(f"   🧮 {len(features_df.columns)} features extraídas")
        
        # Mostrar resumo das features
        self._show_feature_summary(features_df)
        
        # Salvar se especificado
        if output_file:
            features_df.to_csv(output_file, index=False)
            logger.info(f"   💾 Features salvas em: {output_file}")
        
        return features_df
    
    def _show_feature_summary(self, features_df: pd.DataFrame):
        """Mostra resumo das features extraídas"""
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMO DAS FEATURES EXTRAÍDAS")
        logger.info("="*60)
        
        # Contar features por categoria
        categories = {
            'basic': [col for col in features_df.columns if col.startswith('basic_')],
            'chemical': [col for col in features_df.columns if col.startswith('chem_')],
            'spatial': [col for col in features_df.columns if col.startswith('spatial_')],
            'interaction': [col for col in features_df.columns if col.startswith('interact_')],
            'consensus': [col for col in features_df.columns if col.startswith('consensus_')]
        }
        
        for category, features in categories.items():
            logger.info(f"🔹 {category.capitalize()}: {len(features)} features")
            for feature in features[:3]:  # Mostrar primeiras 3
                mean_val = features_df[feature].mean()
                logger.info(f"    • {feature}: μ={mean_val:.3f}")
            if len(features) > 3:
                logger.info(f"    • ... e mais {len(features)-3} features")
        
        logger.info(f"\n🎯 Total: {len(features_df.columns)} features vs. 7 atuais")
        logger.info(f"📈 Melhoria: {len(features_df.columns)/7:.1f}x mais features")
        logger.info("="*60)

def main():
    """Demonstração do extrator de features"""
    
    # Simular dados para demonstração
    demo_poses = [
        {'probe': 'phenol', 'energy': -6.5, 'coordinates': [10.0, 15.0, 20.0]},
        {'probe': 'benzene', 'energy': -5.8, 'coordinates': [12.0, 16.0, 18.0]},
        {'probe': 'ethanol', 'energy': -4.2, 'coordinates': [8.0, 14.0, 22.0]},
        {'probe': 'imidazole', 'energy': -7.1, 'coordinates': [11.0, 17.0, 19.0]}
    ] * 1000  # Simular 4000 poses
    
    # Simular coordenadas da proteína
    protein_coords = np.random.rand(500, 3) * 50  # 500 átomos
    
    # Salvar poses simuladas
    demo_file = 'demo_poses.json'
    with open(demo_file, 'w') as f:
        json.dump({'poses': demo_poses}, f)
    
    # Inicializar extrator
    extractor = FTMapAdvancedFeatureExtractor()
    
    # Processar poses
    features_df = extractor.process_all_poses(demo_file, protein_coords, 'demo_features.csv')
    
    print("\n🎉 Demonstração concluída!")
    print(f"✅ {len(features_df)} poses processadas")
    print(f"🧮 {len(features_df.columns)} features extraídas")
    print("📁 Resultados salvos em: demo_features.csv")

if __name__ == "__main__":
    main()
