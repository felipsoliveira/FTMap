"""
Módulo de Machine Learning
=========================
Implementa ensemble de algoritmos ML para predição de druggability.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import warnings
warnings.filterwarnings('ignore')

from config import FTMapConfig

@dataclass
class MLPrediction:
    """Resultado de predição ML"""
    cluster_id: int
    druggability_score: float
    hotspot_score: float
    confidence: float
    model_contributions: Dict[str, float]

@dataclass
class ModelPerformance:
    """Métricas de performance do modelo"""
    model_name: str
    mse: float
    rmse: float
    mae: float
    r2: float
    cv_score_mean: float
    cv_score_std: float

class MachineLearningPredictor:
    """Classe principal para predições de machine learning"""
    
    def __init__(self, config: Optional[FTMapConfig] = None):
        self.config = config or FTMapConfig()
        self.ml_config = self.config.ml_config
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
    def train_ensemble_models(self, features_df: pd.DataFrame, 
                            target_druggability: Optional[np.ndarray] = None,
                            target_hotspot: Optional[np.ndarray] = None) -> Dict[str, ModelPerformance]:
        """
        Treina ensemble de modelos ML com 29 recursos avançados
        
        Args:
            features_df: DataFrame com os 29 recursos dos clusters
            target_druggability: Alvos de druggability (opcional, usa valores simulados)
            target_hotspot: Alvos de hotspot scores (opcional, usa valores simulados)
            
        Returns:
            Dicionário com performance de cada modelo
        """
        print("🤖 Treinando ensemble de modelos ML com recursos avançados")
        print(f"   📊 Dataset: {len(features_df)} clusters, {len(features_df.columns)-1} features")
        
        # Preparar dados com validação
        X = self._prepare_features(features_df)
        
        # Validar dimensões
        expected_features = 29
        if X.shape[1] != expected_features:
            print(f"⚠️  Features: {X.shape[1]} (esperadas: {expected_features})")
        
        # Gerar alvos se não fornecidos (modo simulação)
        if target_druggability is None or target_hotspot is None:
            print("   🎯 Gerando targets sintéticos baseados em recursos avançados...")
            y_drug, y_hotspot = self._generate_synthetic_targets(features_df)
        else:
            y_drug, y_hotspot = target_druggability, target_hotspot
        
        print(f"   📈 Targets: Druggability [{y_drug.min():.3f}, {y_drug.max():.3f}]")
        print(f"   📈 Targets: Hotspot [{y_hotspot.min():.1f}, {y_hotspot.max():.1f}]")
        
        # Dividir dados com estratificação
        X_train, X_test, y_drug_train, y_drug_test, y_hot_train, y_hot_test = \
            train_test_split(X, y_drug, y_hotspot, test_size=0.2, random_state=42)
        
        print(f"   🔀 Split: Train {X_train.shape[0]}, Test {X_test.shape[0]}")
        
        # Treinar modelos para druggability
        print("   🎯 Treinando modelos para DRUGGABILITY...")
        drug_performance = self._train_models_for_target(
            X_train, X_test, y_drug_train, y_drug_test, 'druggability'
        )
        
        # Treinar modelos para hotspot
        print("   🔥 Treinando modelos para HOTSPOT...")
        hotspot_performance = self._train_models_for_target(
            X_train, X_test, y_hot_train, y_hot_test, 'hotspot'
        )
        
        self.is_trained = True
        
        # Combinar resultados
        all_performance = {**drug_performance, **hotspot_performance}
        
        print("✅ Treinamento concluído!")
        self._print_performance_summary(all_performance)
        
        # Análise de feature importance
        if self.is_trained:
            print("\n🎯 Análise de importância de features:")
            self.print_feature_importance_summary('druggability')
        
        return all_performance
    
    def predict_cluster_properties(self, features_df: pd.DataFrame) -> List[MLPrediction]:
        """
        Faz predições para clusters usando ensemble treinado
        
        Args:
            features_df: DataFrame com features dos clusters
            
        Returns:
            Lista de predições para cada cluster
        """
        if not self.is_trained:
            print("⚠️  Modelos não treinados. Executando treinamento com dados sintéticos...")
            self.train_ensemble_models(features_df)
        
        print(f"🔮 Fazendo predições para {len(features_df)} clusters")
        
        # Preparar features
        X = self._prepare_features(features_df)
        
        predictions = []
        
        for i, row in features_df.iterrows():
            cluster_id = row['cluster_id']
            
            # Predições de druggability
            drug_pred = self._ensemble_predict(X[i:i+1], 'druggability')
            drug_conf = self._calculate_prediction_confidence(X[i:i+1], 'druggability')
            
            # Predições de hotspot
            hotspot_pred = self._ensemble_predict(X[i:i+1], 'hotspot')
            hotspot_conf = self._calculate_prediction_confidence(X[i:i+1], 'hotspot')
            
            # Contribuições dos modelos
            contributions = self._get_model_contributions(X[i:i+1])
            
            # Confiança combinada
            combined_confidence = (drug_conf + hotspot_conf) / 2
            
            prediction = MLPrediction(
                cluster_id=cluster_id,
                druggability_score=float(drug_pred[0]),
                hotspot_score=float(hotspot_pred[0]),
                confidence=float(combined_confidence),
                model_contributions=contributions
            )
            
            predictions.append(prediction)
        
        print(f"✅ Predições concluídas!")
        return predictions
    
    def _prepare_features(self, features_df: pd.DataFrame) -> np.ndarray:
        """Prepara features para ML com os 29 recursos avançados"""
        # Definir ordem exata dos 29 recursos esperados
        expected_features = [
            # Energetic Features (5)
            'mean_affinity', 'std_affinity', 'min_affinity', 'max_affinity', 'energy_range',
            # Spatial Features (9) 
            'center_x', 'center_y', 'center_z', 'spatial_spread', 'volume',
            'surface_area', 'compactness', 'gyration_radius', 'aspect_ratio',
            # Chemical Features (8)
            'molecular_weight', 'logp', 'hbd_count', 'hba_count', 'polar_surface_area',
            'dipole_moment', 'aromatic_ratio', 'polar_ratio',
            # Interaction Features (6)
            'hbond_count', 'vdw_interactions', 'electrostatic_potential', 
            'pi_stacking_potential', 'hydrophobic_contacts', 'charged_interactions',
            # Consensus Features (1)
            'consensus_score'
        ]
        
        # Verificar se temos os recursos esperados
        available_features = [col for col in features_df.columns if col != 'cluster_id']
        
        # Se não temos exatamente 29 features, usar features disponíveis com warning
        if len(available_features) != 29:
            print(f"⚠️  Esperadas 29 features, encontradas {len(available_features)}")
            print(f"   Usando features disponíveis: {available_features[:10]}...")
            feature_columns = available_features
        else:
            # Verificar se temos as features esperadas
            missing_features = [f for f in expected_features if f not in available_features]
            if missing_features:
                print(f"⚠️  Features faltando: {missing_features[:5]}...")
                feature_columns = available_features
            else:
                feature_columns = expected_features
                print(f"✅ Usando todas as 29 features avançadas")
        
        # Extrair matriz de features
        X = features_df[feature_columns].values
        
        # Verificar por valores inválidos
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            print("⚠️  Detectados valores NaN/Inf, aplicando limpeza...")
            X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # Normalizar features usando RobustScaler (mais robusto para outliers)
        if 'feature_scaler' not in self.scalers:
            self.scalers['feature_scaler'] = RobustScaler()
            self.scalers['feature_names'] = feature_columns  # Salvar nomes das features
            X_scaled = self.scalers['feature_scaler'].fit_transform(X)
            print(f"📊 Features normalizadas: {X_scaled.shape}")
        else:
            X_scaled = self.scalers['feature_scaler'].transform(X)
        
        return X_scaled
    
    def _generate_synthetic_targets(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Gera alvos sintéticos avançados baseados nos 29 recursos"""
        n_samples = len(features_df)
        
        druggability = []
        hotspot = []
        
        for _, row in features_df.iterrows():
            # DRUGGABILITY SCORE baseado em múltiplos fatores
            drug_score = 0.3  # Score base
            
            # Fatores energéticos (peso: 35%)
            if 'mean_affinity' in row:
                energy_factor = min(abs(row['mean_affinity']) / 10.0, 0.25)
                drug_score += energy_factor * 0.35
            
            # Fatores químicos (peso: 30%)
            chemical_factor = 0.0
            if 'molecular_weight' in row:
                # MW ideal entre 150-500 Da
                mw_norm = min(row['molecular_weight'] / 500.0, 1.0)
                chemical_factor += mw_norm * 0.1
            if 'logp' in row:
                # LogP ideal entre 1-4
                logp_norm = min(abs(row['logp']) / 5.0, 1.0)
                chemical_factor += logp_norm * 0.1
            if 'polar_surface_area' in row:
                # PSA ideal < 140 Ų
                psa_norm = min(row['polar_surface_area'] / 140.0, 1.0)
                chemical_factor += (1.0 - psa_norm) * 0.1
            drug_score += chemical_factor * 0.30
            
            # Fatores espaciais (peso: 20%)
            spatial_factor = 0.0
            if 'volume' in row:
                volume_norm = min(row['volume'] / 200.0, 1.0)
                spatial_factor += volume_norm * 0.1
            if 'compactness' in row:
                spatial_factor += row['compactness'] * 0.1
            drug_score += spatial_factor * 0.20
            
            # Fatores de interação (peso: 15%)
            interaction_factor = 0.0
            if 'hbond_count' in row:
                hbond_norm = min(row['hbond_count'] / 10.0, 1.0)
                interaction_factor += hbond_norm * 0.075
            if 'hydrophobic_contacts' in row:
                hydro_norm = min(row['hydrophobic_contacts'] / 20.0, 1.0)
                interaction_factor += hydro_norm * 0.075
            drug_score += interaction_factor * 0.15
            
            # Clipping e adição à lista
            drug_score = min(drug_score, 1.0)
            druggability.append(drug_score)
            
            # HOTSPOT SCORE baseado em densidade energética e interações
            hot_score = 5.0  # Score base
            
            # Contribuição energética (40%)
            if 'min_affinity' in row:
                energy_contrib = min(abs(row['min_affinity']) * 2.0, 12.0)
                hot_score += energy_contrib * 0.4
            
            # Contribuição espacial (30%)
            if 'spatial_spread' in row and 'volume' in row:
                density = row['volume'] / max(row['spatial_spread'], 1.0)
                density_contrib = min(density / 10.0, 8.0)
                hot_score += density_contrib * 0.3
            
            # Contribuição de interações (20%)
            if 'vdw_interactions' in row:
                vdw_contrib = min(row['vdw_interactions'] / 5.0, 6.0)
                hot_score += vdw_contrib * 0.2
            
            # Contribuição do consensus (10%)
            if 'consensus_score' in row:
                consensus_contrib = row['consensus_score'] * 3.0
                hot_score += consensus_contrib * 0.1
            
            hotspot.append(hot_score)
        
        # Converter para arrays e adicionar ruído realista
        druggability = np.array(druggability) + np.random.normal(0, 0.03, n_samples)
        hotspot = np.array(hotspot) + np.random.normal(0, 0.8, n_samples)
        
        # Clipping final
        druggability = np.clip(druggability, 0, 1)
        hotspot = np.clip(hotspot, 0, 30)
        
        return druggability, hotspot
    
    def _train_models_for_target(self, X_train: np.ndarray, X_test: np.ndarray,
                               y_train: np.ndarray, y_test: np.ndarray,
                               target_name: str) -> Dict[str, ModelPerformance]:
        """Treina todos os modelos para um alvo específico"""
        
        performance = {}
        
        # Random Forest
        rf_model = RandomForestRegressor(**self.ml_config['random_forest'])
        rf_performance = self._train_single_model(
            rf_model, X_train, X_test, y_train, y_test, f'rf_{target_name}'
        )
        performance[f'RandomForest_{target_name}'] = rf_performance
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(**self.ml_config['gradient_boosting'])
        gb_performance = self._train_single_model(
            gb_model, X_train, X_test, y_train, y_test, f'gb_{target_name}'
        )
        performance[f'GradientBoosting_{target_name}'] = gb_performance
        
        # Neural Network
        nn_model = MLPRegressor(**self.ml_config['neural_network'])
        nn_performance = self._train_single_model(
            nn_model, X_train, X_test, y_train, y_test, f'nn_{target_name}'
        )
        performance[f'NeuralNetwork_{target_name}'] = nn_performance
        
        return performance
    
    def _train_single_model(self, model, X_train: np.ndarray, X_test: np.ndarray,
                          y_train: np.ndarray, y_test: np.ndarray,
                          model_key: str) -> ModelPerformance:
        """Treina um modelo individual"""
        
        # Treinar modelo
        model.fit(X_train, y_train)
        self.models[model_key] = model
        
        # Predições
        y_pred = model.predict(X_test)
        
        # Métricas
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        
        return ModelPerformance(
            model_name=model_key,
            mse=mse,
            rmse=rmse,
            mae=mae,
            r2=r2,
            cv_score_mean=np.mean(cv_scores),
            cv_score_std=np.std(cv_scores)
        )
    
    def _ensemble_predict(self, X: np.ndarray, target_type: str) -> np.ndarray:
        """Faz predição usando ensemble de modelos"""
        
        predictions = []
        weights = self.ml_config['ensemble_weights']
        
        # Predições individuais
        rf_pred = self.models[f'rf_{target_type}'].predict(X)
        gb_pred = self.models[f'gb_{target_type}'].predict(X)
        nn_pred = self.models[f'nn_{target_type}'].predict(X)
        
        # Ensemble com pesos
        ensemble_pred = (weights[0] * rf_pred + 
                        weights[1] * gb_pred + 
                        weights[2] * nn_pred)
        
        return ensemble_pred
    
    def _calculate_prediction_confidence(self, X: np.ndarray, target_type: str) -> float:
        """Calcula confiança da predição baseada na concordância dos modelos"""
        
        rf_pred = self.models[f'rf_{target_type}'].predict(X)[0]
        gb_pred = self.models[f'gb_{target_type}'].predict(X)[0]
        nn_pred = self.models[f'nn_{target_type}'].predict(X)[0]
        
        predictions = [rf_pred, gb_pred, nn_pred]
        
        # Confiança baseada na variância das predições
        variance = np.var(predictions)
        confidence = 1.0 / (1.0 + variance)
        
        return confidence
    
    def _get_model_contributions(self, X: np.ndarray) -> Dict[str, float]:
        """Calcula contribuições de cada modelo"""
        weights = self.ml_config['ensemble_weights']
        
        return {
            'RandomForest': weights[0],
            'GradientBoosting': weights[1],
            'NeuralNetwork': weights[2]
        }
    
    def _print_performance_summary(self, performance: Dict[str, ModelPerformance]):
        """Imprime resumo de performance dos modelos"""
        print("\n📊 Resumo de Performance dos Modelos:")
        print("-" * 60)
        
        for model_name, perf in performance.items():
            print(f"{model_name}:")
            print(f"  R² Score: {perf.r2:.3f}")
            print(f"  RMSE: {perf.rmse:.3f}")
            print(f"  CV Score: {perf.cv_score_mean:.3f} ± {perf.cv_score_std:.3f}")
            print()
    
    def save_models(self, filepath: str):
        """Salva modelos treinados"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'config': self.ml_config,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"✅ Modelos salvos em: {filepath}")
    
    def load_models(self, filepath: str):
        """Carrega modelos salvos"""
        model_data = joblib.load(filepath)
        self.models = model_data['models']
        self.scalers = model_data['scalers']
        self.ml_config = model_data['config']
        self.is_trained = model_data['is_trained']
        print(f"✅ Modelos carregados de: {filepath}")
    
    def get_feature_importance(self, target_type: str = 'druggability') -> Dict[str, float]:
        """Retorna importância das features dos modelos tree-based para 29 recursos"""
        if f'rf_{target_type}' not in self.models:
            return {}
        
        rf_model = self.models[f'rf_{target_type}']
        
        # Usar os nomes das features salvos durante o treinamento
        if 'feature_names' in self.scalers:
            feature_names = self.scalers['feature_names']
        else:
            # Fallback para os 29 recursos esperados
            feature_names = [
                # Energetic Features (5)
                'mean_affinity', 'std_affinity', 'min_affinity', 'max_affinity', 'energy_range',
                # Spatial Features (9) 
                'center_x', 'center_y', 'center_z', 'spatial_spread', 'volume',
                'surface_area', 'compactness', 'gyration_radius', 'aspect_ratio',
                # Chemical Features (8)
                'molecular_weight', 'logp', 'hbd_count', 'hba_count', 'polar_surface_area',
                'dipole_moment', 'aromatic_ratio', 'polar_ratio',
                # Interaction Features (6)
                'hbond_count', 'vdw_interactions', 'electrostatic_potential', 
                'pi_stacking_potential', 'hydrophobic_contacts', 'charged_interactions',
                # Consensus Features (1)
                'consensus_score'
            ]
        
        importance = rf_model.feature_importances_[:len(feature_names)]
        
        # Criar dicionário de importância
        importance_dict = dict(zip(feature_names, importance))
        
        # Ordenar por importância (mais importante primeiro)
        importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        return importance_dict
    
    def get_detailed_feature_analysis(self, target_type: str = 'druggability') -> Dict[str, Any]:
        """Análise detalhada de importância por categoria de features"""
        importance = self.get_feature_importance(target_type)
        
        if not importance:
            return {}
        
        # Categorizar features
        categories = {
            'energetic': ['mean_affinity', 'std_affinity', 'min_affinity', 'max_affinity', 'energy_range'],
            'spatial': ['center_x', 'center_y', 'center_z', 'spatial_spread', 'volume',
                       'surface_area', 'compactness', 'gyration_radius', 'aspect_ratio'],
            'chemical': ['molecular_weight', 'logp', 'hbd_count', 'hba_count', 'polar_surface_area',
                        'dipole_moment', 'aromatic_ratio', 'polar_ratio'],
            'interaction': ['hbond_count', 'vdw_interactions', 'electrostatic_potential', 
                           'pi_stacking_potential', 'hydrophobic_contacts', 'charged_interactions'],
            'consensus': ['consensus_score']
        }
        
        # Calcular importância por categoria
        category_importance = {}
        for category, features in categories.items():
            cat_importance = sum(importance.get(feat, 0) for feat in features if feat in importance)
            category_importance[category] = cat_importance
        
        # Top features globais
        top_features = list(importance.items())[:10]
        
        analysis = {
            'total_features': len(importance),
            'category_importance': category_importance,
            'top_features': top_features,
            'feature_importance': importance
        }
        
        return analysis
    
    def print_feature_importance_summary(self, target_type: str = 'druggability'):
        """Imprime resumo da importância das features"""
        analysis = self.get_detailed_feature_analysis(target_type)
        
        if not analysis:
            print(f"⚠️  Nenhuma análise de importância disponível para {target_type}")
            return
        
        print(f"\n🎯 ANÁLISE DE IMPORTÂNCIA - {target_type.upper()}")
        print("=" * 60)
        
        # Importância por categoria
        print("📊 Importância por Categoria:")
        for category, importance in sorted(analysis['category_importance'].items(), 
                                         key=lambda x: x[1], reverse=True):
            print(f"  {category.capitalize()}: {importance:.3f}")
        
        # Top features
        print(f"\n🔝 Top 10 Features mais importantes:")
        for i, (feature, importance) in enumerate(analysis['top_features'], 1):
            print(f"  {i:2d}. {feature:<25} {importance:.3f}")
        
        print("=" * 60)
    
    def validate_model_robustness(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Valida robustez dos modelos com métricas avançadas"""
        if not self.is_trained:
            print("⚠️  Modelos não treinados. Execute train_ensemble_models() primeiro.")
            return {}
        
        print("🔍 Validando robustez dos modelos...")
        
        X = self._prepare_features(features_df)
        y_drug, y_hotspot = self._generate_synthetic_targets(features_df)
        
        validation_results = {}
        
        # Validação cruzada k-fold
        from sklearn.model_selection import KFold
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        
        for target_type, y in [('druggability', y_drug), ('hotspot', y_hotspot)]:
            target_results = {}
            
            for model_name in ['rf', 'gb', 'nn']:
                model_key = f'{model_name}_{target_type}'
                if model_key not in self.models:
                    continue
                
                model = self.models[model_key]
                
                # Cross-validation scores
                cv_scores = cross_val_score(model, X, y, cv=kf, scoring='r2')
                
                # Stability test (treinar com subsets diferentes)
                stability_scores = []
                for train_idx, val_idx in kf.split(X):
                    X_fold_train, X_fold_val = X[train_idx], X[val_idx]
                    y_fold_train, y_fold_val = y[train_idx], y[val_idx]
                    
                    # Clone do modelo
                    from sklearn.base import clone
                    model_clone = clone(model)
                    model_clone.fit(X_fold_train, y_fold_train)
                    
                    pred = model_clone.predict(X_fold_val)
                    stability_scores.append(r2_score(y_fold_val, pred))
                
                target_results[model_name] = {
                    'cv_mean': np.mean(cv_scores),
                    'cv_std': np.std(cv_scores),
                    'stability_mean': np.mean(stability_scores),
                    'stability_std': np.std(stability_scores)
                }
            
            validation_results[target_type] = target_results
        
        # Ensemble validation
        ensemble_validation = self._validate_ensemble_performance(X, y_drug, y_hotspot)
        validation_results['ensemble'] = ensemble_validation
        
        self._print_validation_summary(validation_results)
        
        return validation_results
    
    def _validate_ensemble_performance(self, X: np.ndarray, y_drug: np.ndarray, y_hotspot: np.ndarray) -> Dict[str, float]:
        """Valida performance do ensemble"""
        
        # Predições do ensemble
        drug_pred = self._ensemble_predict(X, 'druggability')
        hotspot_pred = self._ensemble_predict(X, 'hotspot')
        
        # Métricas do ensemble
        drug_r2 = r2_score(y_drug, drug_pred)
        drug_rmse = np.sqrt(mean_squared_error(y_drug, drug_pred))
        
        hotspot_r2 = r2_score(y_hotspot, hotspot_pred)
        hotspot_rmse = np.sqrt(mean_squared_error(y_hotspot, hotspot_pred))
        
        # Diversidade do ensemble (discordância entre modelos)
        drug_diversity = self._calculate_ensemble_diversity(X, 'druggability')
        hotspot_diversity = self._calculate_ensemble_diversity(X, 'hotspot')
        
        return {
            'druggability_r2': drug_r2,
            'druggability_rmse': drug_rmse,
            'hotspot_r2': hotspot_r2,
            'hotspot_rmse': hotspot_rmse,
            'drug_diversity': drug_diversity,
            'hotspot_diversity': hotspot_diversity
        }
    
    def _calculate_ensemble_diversity(self, X: np.ndarray, target_type: str) -> float:
        """Calcula diversidade do ensemble (maior diversidade = melhor)"""
        
        # Predições individuais
        rf_pred = self.models[f'rf_{target_type}'].predict(X)
        gb_pred = self.models[f'gb_{target_type}'].predict(X)
        nn_pred = self.models[f'nn_{target_type}'].predict(X)
        
        # Calcular variância entre predições
        all_preds = np.column_stack([rf_pred, gb_pred, nn_pred])
        diversity = np.mean(np.var(all_preds, axis=1))
        
        return float(diversity)
    
    def _print_validation_summary(self, validation_results: Dict[str, Any]):
        """Imprime resumo da validação"""
        print("\n📋 RESUMO DA VALIDAÇÃO")
        print("=" * 50)
        
        for target_type in ['druggability', 'hotspot']:
            if target_type not in validation_results:
                continue
                
            print(f"\n🎯 {target_type.upper()}:")
            target_results = validation_results[target_type]
            
            for model_name, metrics in target_results.items():
                print(f"  {model_name.upper()}:")
                print(f"    CV Score: {metrics['cv_mean']:.3f} ± {metrics['cv_std']:.3f}")
                print(f"    Stability: {metrics['stability_mean']:.3f} ± {metrics['stability_std']:.3f}")
        
        # Ensemble results
        if 'ensemble' in validation_results:
            ensemble = validation_results['ensemble']
            print(f"\n🎭 ENSEMBLE:")
            print(f"  Druggability R²: {ensemble['druggability_r2']:.3f}")
            print(f"  Hotspot R²: {ensemble['hotspot_r2']:.3f}")
            print(f"  Drug Diversity: {ensemble['drug_diversity']:.3f}")
            print(f"  Hotspot Diversity: {ensemble['hotspot_diversity']:.3f}")
        
        print("=" * 50)
    
    def get_model_diagnostics(self) -> Dict[str, Any]:
        """Retorna diagnósticos detalhados dos modelos"""
        if not self.is_trained:
            return {}
        
        diagnostics = {
            'models_trained': len(self.models),
            'scalers_fitted': len(self.scalers),
            'feature_names': self.scalers.get('feature_names', []),
            'model_types': list(set(key.split('_')[0] for key in self.models.keys())),
            'target_types': list(set(key.split('_')[1] for key in self.models.keys())),
            'ensemble_weights': self.ml_config.get('ensemble_weights', [])
        }
        
        # Feature importance médio
        if 'feature_names' in self.scalers:
            drug_importance = self.get_feature_importance('druggability')
            hotspot_importance = self.get_feature_importance('hotspot')
            
            diagnostics['feature_importance'] = {
                'druggability': drug_importance,
                'hotspot': hotspot_importance
            }
        
        return diagnostics
