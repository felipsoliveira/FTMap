#!/usr/bin/env python3
"""
FTMap Enhanced - Workflow Manager
Orquestrador principal que coordena todos os módulos do sistema
"""

import os
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple, Any

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent))

from config import FTMapConfig
from protein_preparation import ProteinPreparator
from molecular_docking import ProbeLibrary, MolecularDocker
from clustering_analysis import ClusteringAnalyzer
from feature_extraction import FeatureExtractor
from machine_learning import MachineLearningPredictor
from visualization_reports import VisualizationReports


class FTMapWorkflowManager:
    """
    Gerenciador principal do workflow FTMap Enhanced
    Coordena todos os módulos e gerencia o pipeline completo
    """
    
    def __init__(self, config: Optional[FTMapConfig] = None, output_dir: Optional[str] = None):
        """
        Inicializa o gerenciador de workflow
        
        Args:
            config: Configuração do FTMap (usa padrão se None)
            output_dir: Diretório de saída (cria automático se None)
        """
        self.config = config or FTMapConfig()
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "ftmap_results"
        
        # Criar estrutura de diretórios
        self._setup_directories()
        
        # Configurar logging
        self._setup_logging()
        
        # Inicializar módulos
        self._initialize_modules()
        
        # Estado do workflow
        self.workflow_state = {
            'start_time': None,
            'end_time': None,
            'current_step': None,
            'completed_steps': [],
            'results': {},
            'errors': []
        }
        
        self.logger.info("FTMap Enhanced Workflow Manager inicializado")
        
    def _setup_directories(self):
        """Configura estrutura de diretórios"""
        dirs_to_create = [
            self.output_dir,
            self.output_dir / "prepared_proteins",
            self.output_dir / "docking_results", 
            self.output_dir / "clusters",
            self.output_dir / "features",
            self.output_dir / "models",
            self.output_dir / "reports",
            self.output_dir / "visualizations",
            self.output_dir / "temp",
            self.output_dir / "logs"
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        log_file = self.output_dir / "logs" / f"ftmap_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('FTMapWorkflow')
    
    def _initialize_modules(self):
        """Inicializa todos os módulos do sistema"""
        try:
            self.protein_preparator = ProteinPreparator(self.config)
            self.probe_library = ProbeLibrary(self.config)
            self.molecular_docker = MolecularDocker(self.config)
            self.clustering_analyzer = ClusteringAnalyzer(self.config)
            self.feature_extractor = FeatureExtractor(self.config)
            self.ml_predictor = MachineLearningPredictor(self.config)
            self.visualization_reporter = VisualizationReports(self.config)
            
            self.logger.info("Todos os módulos inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar módulos: {str(e)}")
            raise
    
    def run_complete_workflow(self, protein_file: str, 
                            skip_docking: bool = False,
                            resume_from_step: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa o workflow completo do FTMap Enhanced
        
        Args:
            protein_file: Caminho para o arquivo da proteína
            skip_docking: Se True, pula o docking (usa resultados existentes)
            resume_from_step: Retoma workflow a partir de uma etapa específica
            
        Returns:
            Dicionário com todos os resultados do workflow
        """
        self.workflow_state['start_time'] = time.time()
        self.logger.info(f"🚀 Iniciando workflow FTMap Enhanced para: {protein_file}")
        
        try:
            # Validar entrada
            self._validate_inputs(protein_file)
            
            # Definir steps do workflow
            workflow_steps = [
                ('protein_preparation', self._step_protein_preparation),
                ('docking_execution', self._step_docking_execution),
                ('clustering_analysis', self._step_clustering_analysis),
                ('feature_extraction', self._step_feature_extraction),
                ('ml_prediction', self._step_ml_prediction),
                ('visualization_reports', self._step_visualization_reports)
            ]
            
            # Determinar ponto de início
            start_index = 0
            if resume_from_step:
                start_index = next((i for i, (step, _) in enumerate(workflow_steps) 
                                  if step == resume_from_step), 0)
                self.logger.info(f"Retomando workflow a partir de: {resume_from_step}")
            
            # Executar steps
            workflow_results = {}
            
            for step_name, step_function in workflow_steps[start_index:]:
                if skip_docking and step_name == 'docking_execution':
                    self.logger.info("⏭️  Pulando execução de docking")
                    continue
                
                self.workflow_state['current_step'] = step_name
                self.logger.info(f"🔄 Executando step: {step_name}")
                
                step_start_time = time.time()
                
                try:
                    step_result = step_function(protein_file, workflow_results)
                    workflow_results[step_name] = step_result
                    
                    step_duration = time.time() - step_start_time
                    self.workflow_state['completed_steps'].append({
                        'step': step_name,
                        'duration': step_duration,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.logger.info(f"✅ Step {step_name} concluído em {step_duration:.2f}s")
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro no step {step_name}: {str(e)}")
                    self.workflow_state['errors'].append({
                        'step': step_name,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Decidir se continua ou para
                    if self._is_critical_step(step_name):
                        raise
                    else:
                        self.logger.warning(f"Continuando workflow apesar do erro em {step_name}")
            
            # Finalizar workflow
            self.workflow_state['end_time'] = time.time()
            total_duration = self.workflow_state['end_time'] - self.workflow_state['start_time']
            
            # Compilar resultados finais
            final_results = self._compile_final_results(workflow_results, total_duration)
            
            # Salvar estado do workflow
            self._save_workflow_state(final_results)
            
            self.logger.info(f"🎉 Workflow completo finalizado em {total_duration:.2f}s")
            return final_results
            
        except Exception as e:
            self.logger.error(f"💥 Erro crítico no workflow: {str(e)}")
            self.workflow_state['end_time'] = time.time()
            raise
    
    def _step_protein_preparation(self, protein_file: str, previous_results: Dict) -> Dict:
        """Step 1: Preparação da proteína"""
        self.logger.info("🧬 Preparando proteína...")
        
        protein_id = Path(protein_file).stem
        prepared_protein = self.protein_preparator.prepare_protein(protein_file, protein_id)
        
        # Salvar proteína preparada
        output_file = self.output_dir / "prepared_proteins" / f"{Path(protein_file).stem}_prepared.pdbqt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            'protein_info': prepared_protein,
            'binding_sites': prepared_protein.binding_sites,
            'geometric_properties': {
                'center_of_mass': prepared_protein.center_of_mass,
                'molecular_weight': prepared_protein.molecular_weight,
                'surface_area': prepared_protein.surface_area,
                'cavity_volume': prepared_protein.cavity_volume
            },
            'output_file': str(output_file)
        }
        
        # Salvar metadados
        metadata_file = self.output_dir / "prepared_proteins" / f"{Path(protein_file).stem}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _step_docking_execution(self, protein_file: str, previous_results: Dict) -> Dict:
        """Step 2: Execução do docking molecular"""
        self.logger.info("🎯 Executando docking molecular...")
        
        # Preparar probes
        self.probe_library.ensure_probe_library()
        self.logger.info(f"Preparados {len(self.probe_library.probe_molecules)} probes para docking")
        
        # Executar docking paralelo
        protein_info = previous_results['protein_preparation']['protein_info']
        binding_sites = previous_results['protein_preparation']['binding_sites']
        
        all_poses = []
        if binding_sites:
            # Usar o molecular docker para executar docking
            poses = self.molecular_docker.run_docking_with_probes(
                protein_file, 
                protein_info.pdb_id, 
                binding_sites
            )
            all_poses.extend(poses)
        else:
            self.logger.warning("⚠️  Nenhum sítio de ligação encontrado, gerando poses mock")
            # Gerar poses mock para teste
            for probe in self.probe_library.probe_molecules[:3]:  # Apenas primeiros 3 para teste rápido
                mock_poses = self.molecular_docker._generate_mock_poses(
                    probe, 
                    tuple(protein_info.center_of_mass)
                )
                all_poses.extend(mock_poses)
        
        # Salvar resultados de docking
        docking_file = self.output_dir / "docking_results" / f"{Path(protein_file).stem}_docking.json"
        docking_file.parent.mkdir(parents=True, exist_ok=True)
        
        poses_data = [pose.__dict__ for pose in all_poses]
        with open(docking_file, 'w') as f:
            json.dump(poses_data, f, indent=2)
        
        results = {
            'total_poses': len(all_poses),
            'poses_data': poses_data,
            'probes_used': self.probe_library.probe_molecules,
            'output_file': str(docking_file)
        }
        
        return results
    
    def _step_clustering_analysis(self, protein_file: str, previous_results: Dict) -> Dict:
        """Step 3: Análise de clustering"""
        self.logger.info("🎯 Analisando clusters...")
        
        poses_data = previous_results['docking_execution']['poses_data']
        
        # Converter poses_data para formato adequado se necessário
        if isinstance(poses_data, list) and poses_data:
            # Se poses_data é uma lista de dicts, usar diretamente
            poses_for_clustering = poses_data
        else:
            self.logger.warning("⚠️  Dados de poses inválidos, gerando clusters mock")
            poses_for_clustering = []
        
        # Executar clustering ensemble (método principal)
        final_clusters = self.clustering_analyzer.cluster_poses(poses_for_clustering, method='ensemble')
        
        # Calcular métricas de qualidade
        stability_metrics = self.clustering_analyzer.analyze_cluster_stability(poses_for_clustering)
        
        # Salvar resultados
        clustering_file = self.output_dir / "clustering_results" / f"{Path(protein_file).stem}_clusters.json"
        clustering_file.parent.mkdir(parents=True, exist_ok=True)
        
        clusters_data = [cluster.__dict__ for cluster in final_clusters]
        with open(clustering_file, 'w') as f:
            json.dump({
                'clusters': clusters_data,
                'stability_metrics': stability_metrics,
                'total_clusters': len(final_clusters)
            }, f, indent=2)
        
        results = {
            'final_clusters': final_clusters,
            'stability_metrics': stability_metrics,
            'total_clusters': len(final_clusters),
            'output_file': str(clustering_file)
        }
        
        return results
        
        # Salvar resultados de clustering
        clustering_file = self.output_dir / "clusters" / f"{Path(protein_file).stem}_clusters.json"
        results = {
            'clustering_methods': clustering_results,
            'final_clusters': ensemble_clusters,
            'quality_metrics': quality_metrics,
            'output_file': str(clustering_file)
        }
        
        with open(clustering_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _step_feature_extraction(self, protein_file: str, previous_results: Dict) -> Dict:
        """Step 4: Extração de features"""
        self.logger.info("🧠 Extraindo features avançadas...")
        
        # Verificar se dados necessários estão disponíveis
        if 'clustering_analysis' not in previous_results:
            self.logger.warning("⚠️  Clustering não disponível, gerando features básicas")
            clusters = []
        else:
            clusters = previous_results['clustering_analysis']['final_clusters']
            
        poses_data = previous_results['docking_execution']['poses_data']
        protein_info = previous_results['protein_preparation']['protein_info']
        
        # Extrair features básicas sempre possíveis
        all_features = {}
        
        try:
            # Features energéticas (sempre possível com poses)
            energetic_features = self.feature_extractor.extract_energetic_features(
                clusters, poses_data
            )
            all_features['energetic'] = energetic_features
        except Exception as e:
            self.logger.warning(f"Erro em features energéticas: {e}")
            all_features['energetic'] = {}
        
        try:
            # Features espaciais
            spatial_features = self.feature_extractor.extract_spatial_features(
                clusters, poses_data
            )
            all_features['spatial'] = spatial_features
        except Exception as e:
            self.logger.warning(f"Erro em features espaciais: {e}")
            all_features['spatial'] = {}
        
        # Combinar features disponíveis
        try:
            combined_features = self.feature_extractor.combine_and_normalize_features(all_features)
        except Exception as e:
            self.logger.warning(f"Erro ao combinar features: {e}")
            combined_features = {}
        
        # Salvar features
        features_file = self.output_dir / "features" / f"{Path(protein_file).stem}_features.json"
        features_file.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            'feature_categories': all_features,
            'combined_features': combined_features,
            'feature_count': len(combined_features) if isinstance(combined_features, dict) else 0,
            'output_file': str(features_file)
        }
        
        with open(features_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
        
        # Features espaciais
        spatial_features = self.feature_extractor.extract_spatial_features(
            clusters, poses_data
        )
        all_features['spatial'] = spatial_features
        
        # Features químicas
        chemical_features = self.feature_extractor.extract_chemical_features(
            clusters, poses_data
        )
        all_features['chemical'] = chemical_features
        
        # Features farmacofóricas
        pharmacophoric_features = self.feature_extractor.extract_pharmacophoric_features(
            clusters, poses_data
        )
        all_features['pharmacophoric'] = pharmacophoric_features
        
        # Features de densidade
        density_features = self.feature_extractor.extract_density_features(
            clusters, poses_data, protein_data
        )
        all_features['density'] = density_features
        
        # Features estatísticas
        statistical_features = self.feature_extractor.extract_statistical_features(
            clusters, poses_data
        )
        all_features['statistical'] = statistical_features
        
        # Combinar e normalizar features
        combined_features = self.feature_extractor.combine_and_normalize_features(all_features)
        
        # Salvar features
        features_file = self.output_dir / "features" / f"{Path(protein_file).stem}_features.json"
        results = {
            'feature_categories': all_features,
            'combined_features': combined_features,
            'feature_count': len(combined_features.columns) if hasattr(combined_features, 'columns') else 0,
            'output_file': str(features_file)
        }
        
        with open(features_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _step_ml_prediction(self, protein_file: str, previous_results: Dict) -> Dict:
        """Step 5: Predições com Machine Learning"""
        self.logger.info("🤖 Executando predições ML...")
        
        features = previous_results['feature_extraction']['combined_features']
        clusters = previous_results['clustering_analysis']['final_clusters']
        
        # Treinar modelos ensemble
        self.ml_predictor.train_ensemble_models(features)
        
        # Fazer predições
        druggability_predictions = self.ml_predictor.predict_druggability(features)
        hotspot_scores = self.ml_predictor.predict_hotspot_scores(features)
        binding_affinity = self.ml_predictor.predict_binding_affinity(features)
        
        # Calcular scores de confiança
        confidence_scores = self.ml_predictor.calculate_prediction_confidence(
            features, druggability_predictions
        )
        
        # Ranking final
        final_ranking = self.ml_predictor.rank_binding_sites(
            druggability_predictions, hotspot_scores, confidence_scores
        )
        
        # Salvar modelos e predições
        models_dir = self.output_dir / "models"
        self.ml_predictor.save_models(models_dir)
        
        predictions_file = self.output_dir / "models" / f"{Path(protein_file).stem}_predictions.json"
        results = {
            'druggability_predictions': druggability_predictions,
            'hotspot_scores': hotspot_scores,
            'binding_affinity': binding_affinity,
            'confidence_scores': confidence_scores,
            'final_ranking': final_ranking,
            'models_saved_to': str(models_dir),
            'output_file': str(predictions_file)
        }
        
        with open(predictions_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _step_visualization_reports(self, protein_file: str, previous_results: Dict) -> Dict:
        """Step 6: Visualizações e relatórios"""
        self.logger.info("📊 Gerando visualizações e relatórios...")
        
        # Preparar dados para visualização
        viz_data = {
            'protein_file': protein_file,
            'clusters': previous_results['clustering_analysis']['final_clusters'],
            'features': previous_results['feature_extraction']['combined_features'],
            'predictions': previous_results['ml_prediction'],
            'metadata': {
                'workflow_duration': time.time() - self.workflow_state['start_time'],
                'steps_completed': len(self.workflow_state['completed_steps']),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Gerar relatório HTML
        html_report = self.visualization_reporter.generate_html_report(viz_data)
        html_file = self.output_dir / "reports" / f"{Path(protein_file).stem}_report.html"
        with open(html_file, 'w') as f:
            f.write(html_report)
        
        # Gerar script PyMOL
        pymol_script = self.visualization_reporter.generate_pymol_script(viz_data)
        pymol_file = self.output_dir / "visualizations" / f"{Path(protein_file).stem}_visualization.pml"
        with open(pymol_file, 'w') as f:
            f.write(pymol_script)
        
        # Gerar plots estatísticos
        plots = self.visualization_reporter.generate_statistical_plots(viz_data)
        plots_dir = self.output_dir / "visualizations" / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Exportar dados
        export_data = self.visualization_reporter.export_results(viz_data)
        
        # Salvar dados exportados
        for format_name, data in export_data.items():
            export_file = self.output_dir / "reports" / f"{Path(protein_file).stem}_export.{format_name}"
            if format_name == 'json':
                with open(export_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            elif format_name == 'csv':
                data.to_csv(export_file, index=False)
        
        results = {
            'html_report': str(html_file),
            'pymol_script': str(pymol_file),
            'plots_directory': str(plots_dir),
            'exported_formats': list(export_data.keys()),
            'visualization_files': [str(html_file), str(pymol_file)]
        }
        
        return results
    
    def _validate_inputs(self, protein_file: str):
        """Valida os arquivos de entrada"""
        if not Path(protein_file).exists():
            raise FileNotFoundError(f"Arquivo de proteína não encontrado: {protein_file}")
        
        if not Path(protein_file).suffix.lower() in ['.pdb', '.pdbqt']:
            raise ValueError("Arquivo de proteína deve ser .pdb ou .pdbqt")
    
    def _is_critical_step(self, step_name: str) -> bool:
        """Determina se um step é crítico (workflow para se falhar)"""
        critical_steps = ['protein_preparation', 'docking_execution']
        return step_name in critical_steps
    
    def _compile_final_results(self, workflow_results: Dict, total_duration: float) -> Dict:
        """Compila resultados finais do workflow"""
        return {
            'workflow_metadata': {
                'total_duration': total_duration,
                'start_time': datetime.fromtimestamp(self.workflow_state['start_time']).isoformat(),
                'end_time': datetime.fromtimestamp(self.workflow_state['end_time']).isoformat(),
                'completed_steps': self.workflow_state['completed_steps'],
                'errors': self.workflow_state['errors']
            },
            'results': workflow_results,
            'output_directory': str(self.output_dir),
            'summary': self._generate_results_summary(workflow_results)
        }
    
    def _generate_results_summary(self, workflow_results: Dict) -> Dict:
        """Gera resumo dos resultados"""
        summary = {}
        
        if 'docking_execution' in workflow_results:
            summary['total_poses'] = workflow_results['docking_execution']['total_poses']
            summary['filtered_poses'] = workflow_results['docking_execution'].get('filtered_poses', workflow_results['docking_execution']['total_poses'])
        
        if 'clustering_analysis' in workflow_results:
            summary['clusters_found'] = len(workflow_results['clustering_analysis']['final_clusters'])
        
        if 'feature_extraction' in workflow_results:
            summary['features_extracted'] = workflow_results['feature_extraction']['feature_count']
        
        if 'ml_prediction' in workflow_results:
            predictions = workflow_results['ml_prediction']['final_ranking']
            if predictions:
                summary['top_hotspot_score'] = max(predictions.values()) if predictions else 0
                summary['predicted_druggable_sites'] = len([s for s in predictions.values() if s > 0.7])
        
        return summary
    
    def _save_workflow_state(self, final_results: Dict):
        """Salva estado final do workflow"""
        state_file = self.output_dir / "workflow_state.json"
        with open(state_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        self.logger.info(f"Estado do workflow salvo em: {state_file}")
    
    def get_workflow_status(self) -> Dict:
        """Retorna status atual do workflow"""
        return {
            'current_step': self.workflow_state['current_step'],
            'completed_steps': [step['step'] for step in self.workflow_state['completed_steps']],
            'total_duration': time.time() - self.workflow_state['start_time'] if self.workflow_state['start_time'] else 0,
            'errors': len(self.workflow_state['errors']),
            'output_directory': str(self.output_dir)
        }
    
    def resume_workflow(self, state_file: str, protein_file: str) -> Dict:
        """Resume workflow a partir de estado salvo"""
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        completed_steps = [step['step'] for step in saved_state['workflow_metadata']['completed_steps']]
        
        # Determinar próximo step
        all_steps = ['protein_preparation', 'docking_execution', 'clustering_analysis', 
                    'feature_extraction', 'ml_prediction', 'visualization_reports']
        
        next_step = None
        for step in all_steps:
            if step not in completed_steps:
                next_step = step
                break
        
        if next_step:
            self.logger.info(f"Resumindo workflow a partir de: {next_step}")
            return self.run_complete_workflow(protein_file, resume_from_step=next_step)
        else:
            self.logger.info("Workflow já está completo")
            return saved_state


if __name__ == "__main__":
    # Exemplo de uso básico
    if len(sys.argv) > 1:
        protein_file = sys.argv[1]
        
        # Inicializar workflow manager
        workflow = FTMapWorkflowManager()
        
        # Executar workflow completo
        results = workflow.run_complete_workflow(protein_file)
        
        print(f"\n🎉 Workflow concluído!")
        print(f"📊 Resultados salvos em: {workflow.output_dir}")
        print(f"⏱️  Duração total: {results['workflow_metadata']['total_duration']:.2f}s")
        
    else:
        print("Uso: python workflow_manager.py <arquivo_proteina.pdb>")
