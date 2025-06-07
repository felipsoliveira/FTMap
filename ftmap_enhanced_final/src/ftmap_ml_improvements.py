#!/usr/bin/env python3
"""
FTMap Machine Learning Improvements
Melhorias baseadas em ML para validação e otimização de clusters
"""

import numpy as np
import json
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import pandas as pd
import os

class FTMapMLEnhancer:
    """Melhorias ML para análise FTMap"""
    
    def __init__(self, results_file="enhanced_outputs/ultimate_18probe_analysis/ultimate_18probe_results.json"):
        self.results_file = results_file
        self.cluster_features = []
        self.cluster_labels = []
        
    def extract_cluster_features(self):
        """Extrai features dos clusters para análise ML"""
        print("🧠 Extraindo features dos clusters para análise ML...")
        
        with open(self.results_file, 'r') as f:
            data = json.load(f)
        
        features = []
        for cluster in data['top_clusters'][:50]:  # Top 50 clusters
            cluster_id = cluster['id']
            poses = cluster['poses']
            
            # Features energéticas
            energies = [pose['energy'] for pose in poses]
            energy_features = {
                'min_energy': min(energies),
                'mean_energy': np.mean(energies),
                'energy_std': np.std(energies),
                'energy_range': max(energies) - min(energies)
            }
            
            # Features espaciais
            positions = [[pose['x'], pose['y'], pose['z']] for pose in poses]
            positions = np.array(positions)
            
            spatial_features = {
                'cluster_size': len(poses),
                'spatial_compactness': np.std(positions),
                'center_x': np.mean(positions[:, 0]),
                'center_y': np.mean(positions[:, 1]),
                'center_z': np.mean(positions[:, 2])
            }
            
            # Features de diversidade química
            probe_types = [pose['probe'] for pose in poses]
            diversity_features = {
                'probe_diversity': len(set(probe_types)),
                'dominant_probe_ratio': probe_types.count(max(set(probe_types), key=probe_types.count)) / len(probe_types)
            }
            
            # Combinar todas as features
            cluster_features = {**energy_features, **spatial_features, **diversity_features}
            cluster_features['cluster_id'] = cluster_id
            features.append(cluster_features)
        
        self.cluster_features = pd.DataFrame(features)
        print(f"✅ Extraídas {len(features)} features de {len(features)} clusters")
        return self.cluster_features
    
    def predict_druggability(self):
        """Predição de druggability usando ML"""
        print("🎯 Treinando modelo de predição de druggability...")
        
        if self.cluster_features.empty:
            self.extract_cluster_features()
        
        # Features para treino
        feature_cols = ['min_energy', 'mean_energy', 'energy_std', 'cluster_size', 
                       'spatial_compactness', 'probe_diversity', 'dominant_probe_ratio']
        X = self.cluster_features[feature_cols]
        
        # Target: druggability score baseado em energia + tamanho + diversidade
        y = (
            -self.cluster_features['min_energy'] * 0.4 +  # Energia favorável
            np.log(self.cluster_features['cluster_size']) * 0.3 +  # Tamanho do cluster
            self.cluster_features['probe_diversity'] * 0.3  # Diversidade química
        )
        
        # Treinar modelo
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        # Predições
        predictions = model.predict(X_scaled)
        self.cluster_features['ml_druggability_score'] = predictions
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("📊 Feature Importance:")
        for _, row in feature_importance.iterrows():
            print(f"  {row['feature']}: {row['importance']:.3f}")
        
        return model, scaler, feature_importance
    
    def anomaly_detection(self):
        """Detecção de clusters anômalos/outliers"""
        print("🔍 Detectando clusters anômalos...")
        
        if self.cluster_features.empty:
            self.extract_cluster_features()
        
        feature_cols = ['min_energy', 'mean_energy', 'cluster_size', 'spatial_compactness']
        X = self.cluster_features[feature_cols]
        
        # Normalizar
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Isolation Forest para detecção de anomalias
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        
        self.cluster_features['is_anomaly'] = anomaly_labels == -1
        
        anomalous_clusters = self.cluster_features[self.cluster_features['is_anomaly']]
        print(f"🚨 Detectados {len(anomalous_clusters)} clusters anômalos:")
        
        for _, cluster in anomalous_clusters.iterrows():
            print(f"  Cluster {cluster['cluster_id']}: energia={cluster['min_energy']:.2f}, "
                  f"tamanho={cluster['cluster_size']}")
        
        return anomalous_clusters
    
    def optimal_cluster_validation(self):
        """Validação otimizada do número de clusters usando silhueta"""
        print("🔄 Validando número ótimo de clusters...")
        
        if self.cluster_features.empty:
            self.extract_cluster_features()
        
        feature_cols = ['min_energy', 'mean_energy', 'spatial_compactness', 'probe_diversity']
        X = self.cluster_features[feature_cols]
        
        # Testar diferentes números de clusters
        silhouette_scores = []
        k_range = range(2, min(20, len(X)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            score = silhouette_score(X, cluster_labels)
            silhouette_scores.append(score)
        
        optimal_k = k_range[np.argmax(silhouette_scores)]
        max_score = max(silhouette_scores)
        
        print(f"📈 Número ótimo de clusters: {optimal_k}")
        print(f"📊 Melhor silhouette score: {max_score:.3f}")
        
        return optimal_k, max_score, silhouette_scores
    
    def generate_ml_report(self):
        """Gera relatório completo de análise ML"""
        print("📋 Gerando relatório de análise ML...")
        
        # Executar todas as análises
        self.extract_cluster_features()
        model, scaler, importance = self.predict_druggability()
        anomalous = self.anomaly_detection()
        optimal_k, max_score, scores = self.optimal_cluster_validation()
        
        # Relatório
        report = f"""
RELATÓRIO DE ANÁLISE MACHINE LEARNING - FTMAP
==============================================

RESUMO GERAL:
- Clusters analisados: {len(self.cluster_features)}
- Clusters anômalos detectados: {len(anomalous)}
- Número ótimo de clusters: {optimal_k}
- Score de validação: {max_score:.3f}

TOP 10 CLUSTERS POR ML DRUGGABILITY:
-----------------------------------
"""
        
        top_ml_clusters = self.cluster_features.nlargest(10, 'ml_druggability_score')
        for i, (_, cluster) in enumerate(top_ml_clusters.iterrows(), 1):
            report += f"{i:2d}. Cluster {cluster['cluster_id']:3d}: "
            report += f"ML Score={cluster['ml_druggability_score']:.2f}, "
            report += f"Energia={cluster['min_energy']:.2f} kcal/mol\n"
        
        report += f"""
FEATURE IMPORTANCE:
------------------
"""
        for _, row in importance.iterrows():
            report += f"{row['feature']:<20}: {row['importance']:.3f}\n"
        
        report += f"""
RECOMENDAÇÕES ML:
----------------
1. Focar nos top {min(5, len(top_ml_clusters))} clusters por ML score
2. Investigar {len(anomalous)} clusters anômalos identificados
3. Considerar re-clustering com k={optimal_k} para otimização
4. Monitorar features mais importantes: {importance.iloc[0]['feature']}

PRÓXIMOS PASSOS:
---------------
1. Validação experimental dos clusters ML-otimizados
2. Integração com dados de atividade biológica
3. Modelo preditivo para novos targets
"""
        
        # Salvar relatório
        os.makedirs("enhanced_outputs/ml_analysis", exist_ok=True)
        with open("enhanced_outputs/ml_analysis/ftmap_ml_report.txt", 'w') as f:
            f.write(report)
        
        # Salvar dados para análise posterior
        self.cluster_features.to_csv("enhanced_outputs/ml_analysis/cluster_features.csv", index=False)
        
        print("✅ Relatório ML salvo em: enhanced_outputs/ml_analysis/")
        return report

def main():
    """Executar análise ML completa"""
    print("🚀 FTMap Machine Learning Enhancement")
    print("="*50)
    
    enhancer = FTMapMLEnhancer()
    enhancer.generate_ml_report()
    
    print("\n🎉 Análise ML concluída!")
    print("📁 Resultados em: enhanced_outputs/ml_analysis/")

if __name__ == "__main__":
    main()
