"""
Módulo de Clustering Avançado
============================
Implementa múltiplos algoritmos de clustering e ensemble clustering.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.spatial.distance import pdist, squareform
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

from config import FTMapConfig

@dataclass
class Cluster:
    """Representa um cluster de poses"""
    cluster_id: int
    poses_indices: List[int]
    center: Tuple[float, float, float]
    size: int
    density: float
    avg_affinity: float
    probe_diversity: int
    quality_score: float

class ClusteringAnalyzer:
    """Classe principal para análise de clustering"""
    
    def __init__(self, config: Optional[FTMapConfig] = None):
        self.config = config or FTMapConfig()
        self.clustering_config = self.config.clustering_config
        self.scaler = StandardScaler()
        
    def cluster_poses(self, poses: List, method: str = 'ensemble') -> List[Cluster]:
        """
        Executa clustering das poses de docking
        
        Args:
            poses: Lista de DockingPose objects
            method: Método de clustering ('dbscan', 'hierarchical', 'ensemble')
            
        Returns:
            Lista de clusters identificados
        """
        print(f"🔍 Iniciando clustering com método: {method}")
        print(f"   Total de poses: {len(poses)}")
        
        if len(poses) < 3:
            print("⚠️  Número insuficiente de poses para clustering")
            return []
        
        # Preparar dados para clustering
        features_matrix = self._prepare_clustering_features(poses)
        
        # Executar clustering baseado no método escolhido
        if method == 'dbscan':
            cluster_labels = self._dbscan_clustering(features_matrix)
        elif method == 'hierarchical':
            cluster_labels = self._hierarchical_clustering(features_matrix)
        elif method == 'ensemble':
            cluster_labels = self._ensemble_clustering(features_matrix)
        else:
            raise ValueError(f"Método de clustering desconhecido: {method}")
        
        # Converter labels em objetos Cluster
        clusters = self._create_cluster_objects(poses, cluster_labels)
        
        # Filtrar clusters por tamanho mínimo
        min_size = self.clustering_config['ensemble']['min_cluster_size']
        valid_clusters = [c for c in clusters if c.size >= min_size]
        
        print(f"✅ Clustering concluído!")
        print(f"   Clusters encontrados: {len(valid_clusters)}")
        print(f"   Poses em clusters válidos: {sum(c.size for c in valid_clusters)}")
        
        return valid_clusters
    
    def _prepare_clustering_features(self, poses: List) -> np.ndarray:
        """Prepara matriz de features para clustering"""
        features = []
        
        for pose in poses:
            # Features espaciais
            x, y, z = pose.coordinates
            
            # Features energéticas
            affinity = pose.affinity
            
            # Features de diversidade (encoded)
            probe_encoded = hash(pose.probe_name) % 100
            
            # Features de conformação
            rmsd_avg = (pose.rmsd_lb + pose.rmsd_ub) / 2
            
            feature_vector = [x, y, z, affinity, probe_encoded, rmsd_avg]
            features.append(feature_vector)
        
        features_matrix = np.array(features)
        
        # Normalizar features
        features_normalized = self.scaler.fit_transform(features_matrix)
        
        return features_normalized
    
    def _dbscan_clustering(self, features: np.ndarray) -> np.ndarray:
        """Clustering usando DBSCAN"""
        dbscan_config = self.clustering_config['dbscan']
        
        clustering = DBSCAN(
            eps=dbscan_config['eps'],
            min_samples=dbscan_config['min_samples'],
            metric=dbscan_config['metric']
        )
        
        labels = clustering.fit_predict(features)
        
        # Avaliar qualidade do clustering
        if len(set(labels)) > 1:
            silhouette = silhouette_score(features, labels)
            print(f"   DBSCAN Silhouette Score: {silhouette:.3f}")
        
        return labels
    
    def _hierarchical_clustering(self, features: np.ndarray) -> np.ndarray:
        """Clustering hierárquico"""
        hier_config = self.clustering_config['hierarchical']
        
        clustering = AgglomerativeClustering(
            n_clusters=hier_config['n_clusters'],
            linkage=hier_config['linkage'],
            metric=hier_config['affinity']
        )
        
        labels = clustering.fit_predict(features)
        
        # Avaliar qualidade
        silhouette = silhouette_score(features, labels)
        print(f"   Hierarchical Silhouette Score: {silhouette:.3f}")
        
        return labels
    
    def _ensemble_clustering(self, features: np.ndarray) -> np.ndarray:
        """ENHANCED Ensemble clustering combinando múltiplos métodos (matching original algorithm)"""
        print("   🎯 Executando ENSEMBLE clustering avançado...")
        
        # Executar os 3 algoritmos do sistema original
        dbscan_labels = self._dbscan_clustering(features)
        hier_labels = self._hierarchical_clustering(features)
        agglo_labels = self._agglomerative_clustering(features)
        
        # Combinar resultados usando consenso weighted
        all_labels = [dbscan_labels, hier_labels, agglo_labels]
        weights = self.clustering_config['ensemble']['weights']
        
        consensus_labels = self._weighted_consensus_clustering(all_labels, weights)
        
        # Avaliar qualidade final
        if len(set(consensus_labels)) > 1:
            silhouette = silhouette_score(features, consensus_labels)
            print(f"   Enhanced Ensemble Silhouette Score: {silhouette:.3f}")
            
            # Estatísticas detalhadas
            n_clusters = len(set(consensus_labels)) - (1 if -1 in consensus_labels else 0)
            n_noise = sum(1 for label in consensus_labels if label == -1)
            print(f"   Clusters identificados: {n_clusters}")
            print(f"   Poses classificadas como ruído: {n_noise}")
        
        return consensus_labels
    
    def _agglomerative_clustering(self, features: np.ndarray) -> np.ndarray:
        """Clustering aglomerativo (terceiro algoritmo do ensemble)"""
        agglo_config = self.clustering_config.get('agglomerative', {
            'n_clusters': 10,
            'linkage': 'ward',
            'connectivity': None
        })
        
        clustering = AgglomerativeClustering(
            n_clusters=agglo_config['n_clusters'],
            linkage=agglo_config['linkage'],
            connectivity=agglo_config.get('connectivity')
        )
        
        labels = clustering.fit_predict(features)
        
        # Avaliar qualidade
        silhouette = silhouette_score(features, labels)
        print(f"   Agglomerative Silhouette Score: {silhouette:.3f}")
        
        return labels
    
    def _weighted_consensus_clustering(self, label_sets: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """Cria clustering de consenso WEIGHTED a partir de múltiplos resultados"""
        n_samples = len(label_sets[0])
        consensus_matrix = np.zeros((n_samples, n_samples))
        
        # Construir matriz de consenso weighted
        for labels, weight in zip(label_sets, weights):
            for i in range(n_samples):
                for j in range(i+1, n_samples):
                    if labels[i] == labels[j] and labels[i] != -1:
                        consensus_matrix[i, j] += weight
                        consensus_matrix[j, i] += weight
        
        # Normalizar por soma dos pesos
        consensus_matrix /= sum(weights)
        
        # Aplicar threshold de consenso
        threshold = self.clustering_config['ensemble']['consensus_threshold']
        consensus_matrix = (consensus_matrix >= threshold).astype(int)
        
        # Aplicar clustering final na matriz de consenso
        distance_matrix = 1 - consensus_matrix
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.5,
            linkage='average',
            metric='precomputed'
        )
        
        final_labels = clustering.fit_predict(distance_matrix)
        
        return final_labels
    
    def _create_cluster_objects(self, poses: List, labels: np.ndarray) -> List[Cluster]:
        """Converte labels de clustering em objetos Cluster"""
        clusters = []
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1:  # Ruído
                continue
            
            # Encontrar índices das poses neste cluster
            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            cluster_poses = [poses[i] for i in cluster_indices]
            
            # Calcular propriedades do cluster
            center = self._calculate_cluster_center(cluster_poses)
            avg_affinity = np.mean([pose.affinity for pose in cluster_poses])
            probe_diversity = len(set(pose.probe_name for pose in cluster_poses))
            density = self._calculate_cluster_density(cluster_poses)
            quality_score = self._calculate_cluster_quality(cluster_poses)
            
            cluster = Cluster(
                cluster_id=int(label),
                poses_indices=cluster_indices,
                center=center,
                size=len(cluster_poses),
                density=density,
                avg_affinity=avg_affinity,
                probe_diversity=probe_diversity,
                quality_score=quality_score
            )
            
            clusters.append(cluster)
        
        # Ordenar clusters por qualidade
        clusters.sort(key=lambda c: c.quality_score, reverse=True)
        
        return clusters
    
    def _calculate_cluster_center(self, poses: List) -> Tuple[float, float, float]:
        """Calcula o centro geométrico de um cluster"""
        coordinates = np.array([pose.coordinates for pose in poses])
        center = np.mean(coordinates, axis=0)
        return tuple(center)
    
    def _calculate_cluster_density(self, poses: List) -> float:
        """Calcula a densidade de um cluster"""
        if len(poses) < 2:
            return 0.0
        
        coordinates = np.array([pose.coordinates for pose in poses])
        distances = pdist(coordinates)
        
        avg_distance = np.mean(distances)
        density = len(poses) / (avg_distance + 1e-6)
        
        return density
    
    def _calculate_cluster_quality(self, poses: List) -> float:
        """Calcula score de qualidade do cluster"""
        if len(poses) == 0:
            return 0.0
        
        # Componentes da qualidade
        size_score = min(len(poses) / 10.0, 1.0)  # Normalizado para max 10 poses
        
        energy_score = 1.0 / (1.0 + abs(np.mean([pose.affinity for pose in poses])))
        
        diversity_score = len(set(pose.probe_name for pose in poses)) / len(self.config.probe_molecules)
        
        # Score composto
        quality = 0.4 * size_score + 0.4 * energy_score + 0.2 * diversity_score
        
        return quality
    
    def analyze_cluster_stability(self, poses: List, n_iterations: int = 10) -> Dict[str, float]:
        """Analisa estabilidade do clustering através de múltiplas execuções"""
        print(f"🔄 Analisando estabilidade do clustering ({n_iterations} iterações)")
        
        stability_scores = []
        
        for i in range(n_iterations):
            # Adicionar pequeno ruído aos dados
            features = self._prepare_clustering_features(poses)
            noise = np.random.normal(0, 0.01, features.shape)
            noisy_features = features + noise
            
            # Executar clustering
            labels = self._ensemble_clustering(noisy_features)
            
            if i > 0:
                # Comparar com clustering anterior
                ari_score = adjusted_rand_score(previous_labels, labels)
                stability_scores.append(ari_score)
            
            previous_labels = labels
        
        stability_stats = {
            'mean_stability': np.mean(stability_scores),
            'std_stability': np.std(stability_scores),
            'min_stability': np.min(stability_scores),
            'max_stability': np.max(stability_scores)
        }
        
        print(f"   Estabilidade média: {stability_stats['mean_stability']:.3f}")
        
        return stability_stats
