#!/usr/bin/env python3
"""
Módulo de Visualização e Relatórios - FTMap Enhanced Modular
Responsável por gerar visualizações, relatórios e arquivos de saída
"""

import numpy as np
import pandas as pd
import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

# Configurar matplotlib para backend não-interativo
import matplotlib
matplotlib.use('Agg')

@dataclass
class VisualizationConfig:
    """Configurações para visualização"""
    output_format: str = 'both'  # 'html', 'pymol', 'both'
    figure_dpi: int = 300
    figure_size: tuple = (12, 8)
    color_scheme: str = 'viridis'
    save_figures: bool = True
    pymol_style: str = 'cartoon'

@dataclass
class ReportData:
    """Estrutura de dados para relatório"""
    protein_name: str
    execution_time: float
    total_poses: int
    total_clusters: int
    top_hotspots: List[Dict]
    statistics: Dict[str, Any]
    metadata: Dict[str, Any]

class VisualizationReports:
    """Classe principal para visualização e relatórios"""
    
    def __init__(self, config = None):
        self.config = config or VisualizationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Configurar estilo de plotagem
        plt.style.use('seaborn-v0_8')
        sns.set_palette(self.config.color_scheme)
        
    def generate_comprehensive_report(self, features_df: pd.DataFrame, 
                                    protein_info: Dict, 
                                    docking_results: List[Dict],
                                    output_dir: Path) -> Dict[str, str]:
        """Gera relatório completo com visualizações"""
        self.logger.info("🎨 Gerando relatório completo com visualizações...")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Dados do relatório
        report_data = self._prepare_report_data(features_df, protein_info, docking_results)
        
        # Gerar visualizações
        figures_dict = self._generate_all_visualizations(features_df, output_dir)
        
        # Gerar relatórios
        reports = {}
        
        if self.config.output_format in ['html', 'both']:
            html_report = self._generate_html_report(report_data, figures_dict, output_dir)
            reports['html'] = html_report
            
        if self.config.output_format in ['pymol', 'both']:
            pymol_script = self._generate_pymol_script(features_df, protein_info, output_dir)
            reports['pymol'] = pymol_script
            
        # Gerar arquivos de dados
        self._generate_data_files(features_df, report_data, output_dir)
        
        # Gerar resumo executivo
        summary_report = self._generate_executive_summary(report_data, output_dir)
        reports['summary'] = summary_report
        
        self.logger.info(f"✅ Relatório completo gerado em: {output_dir}")
        return reports
    
    def _prepare_report_data(self, features_df: pd.DataFrame, 
                           protein_info: Dict, 
                           docking_results: List[Dict]) -> ReportData:
        """Prepara dados para o relatório"""
        
        # Top hotspots (top 10)
        top_hotspots = []
        if not features_df.empty:
            top_clusters = features_df.nlargest(10, 'druggability_index')
            for _, cluster in top_clusters.iterrows():
                hotspot = {
                    'cluster_id': int(cluster['cluster_id']),
                    'druggability_index': float(cluster['druggability_index']),
                    'hotspot_score': float(cluster['hotspot_score']),
                    'min_energy': float(cluster['min_energy']),
                    'cluster_size': int(cluster['cluster_size']),
                    'probe_diversity': int(cluster['probe_diversity']),
                    'center_coordinates': [float(cluster['center_x']), 
                                         float(cluster['center_y']), 
                                         float(cluster['center_z'])],
                    'category': cluster.get('cluster_category', 'Unknown')
                }
                top_hotspots.append(hotspot)
        
        # Estatísticas gerais
        statistics = {
            'total_clusters': len(features_df) if not features_df.empty else 0,
            'high_druggability_clusters': len(features_df[features_df['druggability_index'] >= 0.7]) if not features_df.empty else 0,
            'exceptional_hotspots': len(features_df[features_df.get('is_exceptional_hotspot', False) == True]) if not features_df.empty else 0,
            'mean_druggability': float(features_df['druggability_index'].mean()) if not features_df.empty else 0.0,
            'energy_range': {
                'min': float(features_df['min_energy'].min()) if not features_df.empty else 0.0,
                'max': float(features_df['min_energy'].max()) if not features_df.empty else 0.0,
                'mean': float(features_df['min_energy'].mean()) if not features_df.empty else 0.0
            }
        }
        
        # Metadata
        metadata = {
            'analysis_date': datetime.now().isoformat(),
            'protein_file': protein_info.get('original_file', 'Unknown'),
            'algorithm_version': 'FTMap Enhanced Modular v1.0',
            'total_features_extracted': len(features_df.columns) if not features_df.empty else 0
        }
        
        return ReportData(
            protein_name=Path(protein_info.get('original_file', 'Unknown')).stem,
            execution_time=protein_info.get('execution_time', 0.0),
            total_poses=len(docking_results),
            total_clusters=len(features_df) if not features_df.empty else 0,
            top_hotspots=top_hotspots,
            statistics=statistics,
            metadata=metadata
        )
    
    def _generate_all_visualizations(self, features_df: pd.DataFrame, 
                                   output_dir: Path) -> Dict[str, str]:
        """Gera todas as visualizações"""
        figures_dict = {}
        
        if features_df.empty:
            self.logger.warning("DataFrame vazio, pulando visualizações")
            return figures_dict
        
        # 1. Gráfico de dispersão druggability vs energia
        fig_path = self._plot_druggability_vs_energy(features_df, output_dir)
        figures_dict['druggability_energy'] = fig_path
        
        # 2. Distribuição de clusters por categoria
        fig_path = self._plot_cluster_distribution(features_df, output_dir)
        figures_dict['cluster_distribution'] = fig_path
        
        # 3. Heatmap de correlação de features
        fig_path = self._plot_feature_correlation(features_df, output_dir)
        figures_dict['feature_correlation'] = fig_path
        
        # 4. Box plot de energias por categoria
        fig_path = self._plot_energy_by_category(features_df, output_dir)
        figures_dict['energy_categories'] = fig_path
        
        # 5. Gráfico 3D de clusters principais
        fig_path = self._plot_3d_clusters(features_df, output_dir)
        figures_dict['clusters_3d'] = fig_path
        
        # 6. Gráfico de ranking de hotspots
        fig_path = self._plot_hotspot_ranking(features_df, output_dir)
        figures_dict['hotspot_ranking'] = fig_path
        
        # 7. Análise de diversidade química
        fig_path = self._plot_chemical_diversity(features_df, output_dir)
        figures_dict['chemical_diversity'] = fig_path
        
        # 8. Mapa de features importantes
        fig_path = self._plot_feature_importance(features_df, output_dir)
        figures_dict['feature_importance'] = fig_path
        
        return figures_dict
    
    def _plot_druggability_vs_energy(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Gráfico de dispersão: Druggability Index vs Energia"""
        fig, ax = plt.subplots(figsize=self.config.figure_size, dpi=self.config.figure_dpi)
        
        # Scatter plot com cores baseadas no tamanho do cluster
        scatter = ax.scatter(df['min_energy'], df['druggability_index'], 
                           c=df['cluster_size'], s=60, alpha=0.7, 
                           cmap=self.config.color_scheme)
        
        # Adicionar colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Tamanho do Cluster', rotation=270, labelpad=20)
        
        # Destacar clusters excepcionais
        if 'is_exceptional_hotspot' in df.columns:
            exceptional = df[df['is_exceptional_hotspot'] == True]
            if not exceptional.empty:
                ax.scatter(exceptional['min_energy'], exceptional['druggability_index'],
                          s=100, color='red', marker='*', label='Hotspots Excepcionais')
                ax.legend()
        
        ax.set_xlabel('Energia Mínima (kcal/mol)')
        ax.set_ylabel('Índice de Druggability')
        ax.set_title('Druggability Index vs Energia Mínima dos Clusters')
        ax.grid(True, alpha=0.3)
        
        # Adicionar linhas de referência
        ax.axhline(y=0.7, color='r', linestyle='--', alpha=0.5, label='Alto Potencial')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Médio Potencial')
        ax.axvline(x=-6.0, color='g', linestyle='--', alpha=0.5, label='Energia Favorável')
        
        plt.tight_layout()
        
        output_path = output_dir / 'druggability_vs_energy.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_cluster_distribution(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Gráfico de distribuição de clusters por categoria"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=self.config.figure_dpi)
        
        # Gráfico de pizza - distribuição por categoria
        if 'cluster_category' in df.columns:
            category_counts = df['cluster_category'].value_counts()
            colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
            
            ax1.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
                   colors=colors, startangle=90)
            ax1.set_title('Distribuição de Clusters por Categoria')
        
        # Histograma - distribuição de druggability
        ax2.hist(df['druggability_index'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.axvline(df['druggability_index'].mean(), color='red', linestyle='--', 
                   label=f'Média: {df["druggability_index"].mean():.3f}')
        ax2.set_xlabel('Índice de Druggability')
        ax2.set_ylabel('Número de Clusters')
        ax2.set_title('Distribuição do Índice de Druggability')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = output_dir / 'cluster_distribution.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_feature_correlation(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Heatmap de correlação entre features principais"""
        # Selecionar features numéricas principais
        numeric_cols = ['min_energy', 'cluster_size', 'druggability_index', 'hotspot_score',
                       'probe_diversity', 'compactness', 'density', 'consensus_score']
        
        available_cols = [col for col in numeric_cols if col in df.columns]
        if len(available_cols) < 2:
            self.logger.warning("Poucas colunas numéricas para correlação")
            return ""
        
        correlation_matrix = df[available_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8), dpi=self.config.figure_dpi)
        
        # Heatmap
        sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0,
                   square=True, ax=ax, cbar_kws={'label': 'Correlação'})
        
        ax.set_title('Matriz de Correlação - Features Principais')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        output_path = output_dir / 'feature_correlation.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_energy_by_category(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Box plot de energias por categoria"""
        if 'cluster_category' not in df.columns:
            return ""
        
        fig, ax = plt.subplots(figsize=self.config.figure_size, dpi=self.config.figure_dpi)
        
        # Box plot
        sns.boxplot(data=df, x='cluster_category', y='min_energy', ax=ax)
        
        # Adicionar pontos individuais
        sns.stripplot(data=df, x='cluster_category', y='min_energy', 
                     color='red', alpha=0.5, size=4, ax=ax)
        
        ax.set_xlabel('Categoria do Cluster')
        ax.set_ylabel('Energia Mínima (kcal/mol)')
        ax.set_title('Distribuição de Energias por Categoria de Cluster')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = output_dir / 'energy_by_category.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_3d_clusters(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Gráfico 3D dos clusters principais"""
        if not all(col in df.columns for col in ['center_x', 'center_y', 'center_z']):
            return ""
        
        fig = plt.figure(figsize=self.config.figure_size, dpi=self.config.figure_dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # Top 20 clusters para visualização
        top_clusters = df.nlargest(20, 'druggability_index')
        
        # Scatter 3D
        scatter = ax.scatter(top_clusters['center_x'], 
                           top_clusters['center_y'], 
                           top_clusters['center_z'],
                           c=top_clusters['druggability_index'],
                           s=top_clusters['cluster_size']*2,
                           alpha=0.7, cmap=self.config.color_scheme)
        
        # Colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Druggability Index', rotation=270, labelpad=20)
        
        ax.set_xlabel('X (Å)')
        ax.set_ylabel('Y (Å)')
        ax.set_zlabel('Z (Å)')
        ax.set_title('Localização 3D dos Top Clusters')
        
        output_path = output_dir / 'clusters_3d.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_hotspot_ranking(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Gráfico de ranking dos hotspots"""
        # Top 15 hotspots
        top_hotspots = df.nlargest(15, 'druggability_index')
        
        fig, ax = plt.subplots(figsize=(12, 8), dpi=self.config.figure_dpi)
        
        # Gráfico de barras
        bars = ax.barh(range(len(top_hotspots)), top_hotspots['druggability_index'],
                      color=plt.cm.viridis(top_hotspots['druggability_index']))
        
        # Labels
        ax.set_yticks(range(len(top_hotspots)))
        ax.set_yticklabels([f"Cluster {int(cid)}" for cid in top_hotspots['cluster_id']])
        ax.set_xlabel('Druggability Index')
        ax.set_title('Ranking dos Top Hotspots')
        
        # Adicionar valores nas barras
        for i, (bar, value) in enumerate(zip(bars, top_hotspots['druggability_index'])):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{value:.3f}', va='center', ha='left', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        output_path = output_dir / 'hotspot_ranking.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_chemical_diversity(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Análise de diversidade química"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12), dpi=self.config.figure_dpi)
        
        # 1. Diversidade de probes
        if 'probe_diversity' in df.columns:
            ax1.hist(df['probe_diversity'], bins=10, alpha=0.7, color='lightblue', edgecolor='black')
            ax1.set_xlabel('Diversidade de Probes')
            ax1.set_ylabel('Número de Clusters')
            ax1.set_title('Distribuição da Diversidade Química')
            ax1.grid(True, alpha=0.3)
        
        # 2. Ratios farmacofóricos
        pharmacophore_cols = ['hydrophobic_ratio', 'polar_ratio', 'aromatic_ratio', 'hbond_donor_ratio']
        available_pharm_cols = [col for col in pharmacophore_cols if col in df.columns]
        
        if available_pharm_cols:
            pharm_data = df[available_pharm_cols].mean()
            ax2.pie(pharm_data.values, labels=[col.replace('_ratio', '').title() for col in pharm_data.index],
                   autopct='%1.1f%%', startangle=90)
            ax2.set_title('Composição Farmacofórica Média')
        
        # 3. Druggability vs Diversidade
        if 'probe_diversity' in df.columns:
            ax3.scatter(df['probe_diversity'], df['druggability_index'], alpha=0.6)
            ax3.set_xlabel('Diversidade de Probes')
            ax3.set_ylabel('Druggability Index')
            ax3.set_title('Druggability vs Diversidade Química')
            ax3.grid(True, alpha=0.3)
        
        # 4. Score farmacofórico
        if 'pharmacophore_score' in df.columns:
            ax4.hist(df['pharmacophore_score'], bins=15, alpha=0.7, color='lightcoral', edgecolor='black')
            ax4.set_xlabel('Score Farmacofórico')
            ax4.set_ylabel('Número de Clusters')
            ax4.set_title('Distribuição do Score Farmacofórico')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = output_dir / 'chemical_diversity.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _plot_feature_importance(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Mapa de importância de features"""
        # Selecionar features principais para análise
        important_features = [
            'min_energy', 'cluster_size', 'druggability_index', 'hotspot_score',
            'probe_diversity', 'compactness', 'density', 'consensus_score',
            'surface_accessibility', 'pharmacophore_score'
        ]
        
        available_features = [f for f in important_features if f in df.columns]
        
        if len(available_features) < 3:
            return ""
        
        # Calcular variância normalizada como proxy para importância
        feature_importance = df[available_features].var().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 8), dpi=self.config.figure_dpi)
        
        # Gráfico de barras horizontal
        bars = ax.barh(range(len(feature_importance)), feature_importance.values,
                      color=plt.cm.plasma(np.linspace(0, 1, len(feature_importance))))
        
        ax.set_yticks(range(len(feature_importance)))
        ax.set_yticklabels([f.replace('_', ' ').title() for f in feature_importance.index])
        ax.set_xlabel('Variância (Importância Relativa)')
        ax.set_title('Importância Relativa das Features')
        
        # Adicionar valores
        for bar, value in zip(bars, feature_importance.values):
            ax.text(bar.get_width() + value*0.01, bar.get_y() + bar.get_height()/2,
                   f'{value:.3f}', va='center', ha='left', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        output_path = output_dir / 'feature_importance.png'
        plt.savefig(output_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _generate_html_report(self, report_data: ReportData, 
                            figures_dict: Dict[str, str], 
                            output_dir: Path) -> str:
        """Gera relatório HTML completo"""
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FTMap Enhanced - Relatório de Análise</title>
    <style>
        body {{ 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f8f9fa; 
            color: #333;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            text-align: center;
        }}
        .header h1 {{ 
            margin: 0; 
            font-size: 2.5em; 
            font-weight: bold;
        }}
        .header p {{ 
            margin: 10px 0 0 0; 
            font-size: 1.2em; 
            opacity: 0.9;
        }}
        .content {{ 
            padding: 30px;
        }}
        .section {{ 
            margin-bottom: 40px; 
            border-bottom: 2px solid #eee; 
            padding-bottom: 30px;
        }}
        .section:last-child {{ 
            border-bottom: none;
        }}
        .section h2 {{ 
            color: #667eea; 
            border-left: 4px solid #667eea; 
            padding-left: 15px; 
            margin-bottom: 20px;
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }}
        .stat-card {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            border-left: 4px solid #667eea; 
            text-align: center;
        }}
        .stat-card h3 {{ 
            margin: 0 0 10px 0; 
            color: #667eea; 
            font-size: 1.1em;
        }}
        .stat-card .value {{ 
            font-size: 2em; 
            font-weight: bold; 
            color: #333;
        }}
        .hotspot-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
        }}
        .hotspot-table th, .hotspot-table td {{ 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd;
        }}
        .hotspot-table th {{ 
            background-color: #667eea; 
            color: white; 
            font-weight: bold;
        }}
        .hotspot-table tr:nth-child(even) {{ 
            background-color: #f8f9fa;
        }}
        .hotspot-table tr:hover {{ 
            background-color: #e3f2fd;
        }}
        .figure-container {{ 
            text-align: center; 
            margin: 20px 0;
        }}
        .figure-container img {{ 
            max-width: 100%; 
            height: auto; 
            border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .figure-caption {{ 
            margin-top: 10px; 
            font-style: italic; 
            color: #666; 
            font-size: 0.9em;
        }}
        .badge {{ 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 0.8em; 
            font-weight: bold;
        }}
        .badge-high {{ 
            background-color: #28a745; 
            color: white;
        }}
        .badge-medium {{ 
            background-color: #ffc107; 
            color: #333;
        }}
        .badge-low {{ 
            background-color: #dc3545; 
            color: white;
        }}
        .coordinates {{ 
            font-family: 'Courier New', monospace; 
            font-size: 0.9em; 
            background-color: #f1f1f1; 
            padding: 2px 6px; 
            border-radius: 3px;
        }}
        .footer {{ 
            background-color: #f8f9fa; 
            padding: 20px; 
            text-align: center; 
            color: #666; 
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 FTMap Enhanced</h1>
            <p>Relatório de Análise Completa - {protein_name}</p>
            <p>Gerado em: {analysis_date}</p>
        </div>
        
        <div class="content">
            <!-- Resumo Executivo -->
            <div class="section">
                <h2>📊 Resumo Executivo</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total de Poses</h3>
                        <div class="value">{total_poses:,}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Clusters Identificados</h3>
                        <div class="value">{total_clusters}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Hotspots de Alto Potencial</h3>
                        <div class="value">{high_druggability_clusters}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Hotspots Excepcionais</h3>
                        <div class="value">{exceptional_hotspots}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Druggability Média</h3>
                        <div class="value">{mean_druggability:.3f}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Tempo de Execução</h3>
                        <div class="value">{execution_time:.1f}s</div>
                    </div>
                </div>
            </div>
            
            <!-- Top Hotspots -->
            <div class="section">
                <h2>🎯 Top Hotspots Identificados</h2>
                <table class="hotspot-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Cluster ID</th>
                            <th>Druggability</th>
                            <th>Hotspot Score</th>
                            <th>Energia (kcal/mol)</th>
                            <th>Tamanho</th>
                            <th>Diversidade</th>
                            <th>Coordenadas</th>
                            <th>Categoria</th>
                        </tr>
                    </thead>
                    <tbody>
                        {hotspots_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Visualizações -->
            <div class="section">
                <h2>📈 Análises Visuais</h2>
                
                {visualization_sections}
            </div>
            
            <!-- Estatísticas Detalhadas -->
            <div class="section">
                <h2>📋 Estatísticas Detalhadas</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Energia Mínima</h3>
                        <div class="value">{energy_min:.2f} kcal/mol</div>
                    </div>
                    <div class="stat-card">
                        <h3>Energia Máxima</h3>
                        <div class="value">{energy_max:.2f} kcal/mol</div>
                    </div>
                    <div class="stat-card">
                        <h3>Energia Média</h3>
                        <div class="value">{energy_mean:.2f} kcal/mol</div>
                    </div>
                    <div class="stat-card">
                        <h3>Features Extraídas</h3>
                        <div class="value">{total_features_extracted}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>FTMap Enhanced Modular v1.0</strong> | 
               Algoritmo avançado de identificação de hotspots | 
               Gerado automaticamente</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Preparar dados para o template
        hotspots_rows = ""
        for i, hotspot in enumerate(report_data.top_hotspots, 1):
            category = hotspot['category']
            badge_class = f"badge-{category.lower()}" if category.lower() in ['high', 'medium', 'low'] else "badge-medium"
            
            coords = hotspot['center_coordinates']
            coord_str = f"({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f})"
            
            hotspots_rows += f"""
                <tr>
                    <td><strong>{i}</strong></td>
                    <td>Cluster {hotspot['cluster_id']}</td>
                    <td>{hotspot['druggability_index']:.3f}</td>
                    <td>{hotspot['hotspot_score']:.3f}</td>
                    <td>{hotspot['min_energy']:.2f}</td>
                    <td>{hotspot['cluster_size']}</td>
                    <td>{hotspot['probe_diversity']}</td>
                    <td class="coordinates">{coord_str}</td>
                    <td><span class="badge {badge_class}">{category}</span></td>
                </tr>
            """
        
        # Preparar seções de visualização
        visualization_sections = ""
        viz_info = {
            'druggability_energy': ('Druggability vs Energia', 'Correlação entre o índice de druggability e energia de binding'),
            'cluster_distribution': ('Distribuição de Clusters', 'Distribuição estatística dos clusters identificados'),
            'feature_correlation': ('Correlação de Features', 'Matriz de correlação entre as principais features'),
            'energy_categories': ('Energias por Categoria', 'Distribuição de energias agrupadas por categoria'),
            'clusters_3d': ('Localização 3D', 'Visualização espacial dos principais clusters'),
            'hotspot_ranking': ('Ranking de Hotspots', 'Classificação dos melhores hotspots identificados'),
            'chemical_diversity': ('Diversidade Química', 'Análise da composição química dos clusters'),
            'feature_importance': ('Importância de Features', 'Relevância relativa das diferentes características')
        }
        
        for fig_key, fig_path in figures_dict.items():
            if fig_path and Path(fig_path).exists():
                title, description = viz_info.get(fig_key, (fig_key.replace('_', ' ').title(), 'Análise visual'))
                
                # Caminho relativo para a imagem
                relative_path = Path(fig_path).name
                
                visualization_sections += f"""
                    <h3>{title}</h3>
                    <div class="figure-container">
                        <img src="{relative_path}" alt="{title}">
                        <div class="figure-caption">{description}</div>
                    </div>
                """
        
        # Preencher template
        html_content = html_template.format(
            protein_name=report_data.protein_name,
            analysis_date=datetime.fromisoformat(report_data.metadata['analysis_date']).strftime('%d/%m/%Y %H:%M:%S'),
            total_poses=report_data.total_poses,
            total_clusters=report_data.total_clusters,
            high_druggability_clusters=report_data.statistics['high_druggability_clusters'],
            exceptional_hotspots=report_data.statistics['exceptional_hotspots'],
            mean_druggability=report_data.statistics['mean_druggability'],
            execution_time=report_data.execution_time,
            hotspots_rows=hotspots_rows,
            visualization_sections=visualization_sections,
            energy_min=report_data.statistics['energy_range']['min'],
            energy_max=report_data.statistics['energy_range']['max'],
            energy_mean=report_data.statistics['energy_range']['mean'],
            total_features_extracted=report_data.metadata['total_features_extracted']
        )
        
        # Salvar arquivo HTML
        html_path = output_dir / 'ftmap_enhanced_report.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_path)
    
    def _generate_pymol_script(self, features_df: pd.DataFrame, 
                             protein_info: Dict, 
                             output_dir: Path) -> str:
        """Gera script PyMOL para visualização 3D"""
        if features_df.empty:
            return ""
        
        # Top 20 clusters para visualização
        top_clusters = features_df.nlargest(20, 'druggability_index')
        
        pymol_script = f"""# FTMap Enhanced - Script PyMOL
# Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
# Proteína: {protein_info.get('original_file', 'Unknown')}

# Configurações iniciais
reinitialize
bg_color white
set depth_cue, off
set ray_trace_mode, 1
set ray_shadows, off

# Carregar proteína
load {protein_info.get('original_file', 'protein.pdb')}, protein
show cartoon, protein
color gray80, protein

# Configurar representação
set cartoon_transparency, 0.3
show surface, protein
set surface_mode, 2
set transparency, 0.7

# Hotspots por categoria
"""
        
        # Cores por categoria
        color_map = {
            'High': 'red',
            'Medium': 'orange', 
            'Low': 'yellow',
            'Unknown': 'gray'
        }
        
        # Adicionar hotspots
        for _, cluster in top_clusters.iterrows():
            cluster_id = int(cluster['cluster_id'])
            x, y, z = cluster['center_x'], cluster['center_y'], cluster['center_z']
            category = cluster.get('cluster_category', 'Unknown')
            color = color_map.get(category, 'gray')
            druggability = cluster['druggability_index']
            
            # Raio baseado no druggability (min 2.0, max 8.0)
            radius = 2.0 + (druggability * 6.0)
            
            pymol_script += f"""
# Cluster {cluster_id} - {category} (Druggability: {druggability:.3f})
pseudoatom hotspot_{cluster_id}, pos=[{x:.2f}, {y:.2f}, {z:.2f}]
show spheres, hotspot_{cluster_id}
set sphere_scale, {radius:.2f}, hotspot_{cluster_id}
color {color}, hotspot_{cluster_id}
set sphere_transparency, 0.3, hotspot_{cluster_id}
"""
        
        # Adicionar labels
        pymol_script += """
# Labels para os top 5 hotspots
"""
        
        top_5 = top_clusters.head(5)
        for i, (_, cluster) in enumerate(top_5.iterrows(), 1):
            cluster_id = int(cluster['cluster_id'])
            druggability = cluster['druggability_index']
            
            pymol_script += f"""
label hotspot_{cluster_id}, "#{i}\\nD:{druggability:.3f}"
set label_color, black, hotspot_{cluster_id}
set label_size, 14, hotspot_{cluster_id}
"""
        
        # Configurações finais
        pymol_script += """
# Configurações de visualização
center protein
zoom protein
orient
set ray_trace_mode, 1

# Salvar imagem
ray 1200, 900
png ftmap_enhanced_visualization.png, dpi=300

# Salvar sessão
save ftmap_enhanced_session.pse

print "Visualização FTMap Enhanced carregada!"
print "Hotspots identificados por cores:"
print "  Vermelho: Alto potencial (High)"
print "  Laranja: Médio potencial (Medium)" 
print "  Amarelo: Baixo potencial (Low)"
print "Tamanho das esferas proporcional ao druggability index"
"""
        
        # Salvar script
        pymol_path = output_dir / 'ftmap_enhanced_visualization.pml'
        with open(pymol_path, 'w') as f:
            f.write(pymol_script)
        
        return str(pymol_path)
    
    def _generate_data_files(self, features_df: pd.DataFrame, 
                           report_data: ReportData, 
                           output_dir: Path):
        """Gera arquivos de dados para análises posteriores"""
        
        # 1. CSV com todas as features
        if not features_df.empty:
            csv_path = output_dir / 'ftmap_enhanced_features.csv'
            features_df.to_csv(csv_path, index=False)
        
        # 2. JSON com dados do relatório
        json_path = output_dir / 'ftmap_enhanced_report_data.json'
        with open(json_path, 'w') as f:
            json.dump(asdict(report_data), f, indent=2, default=str)
        
        # 3. PDB com clusters (top 10)
        if not features_df.empty:
            self._generate_clusters_pdb(features_df.head(10), output_dir)
        
        # 4. Arquivo de resumo em texto
        self._generate_text_summary(report_data, output_dir)
    
    def _generate_clusters_pdb(self, top_clusters: pd.DataFrame, output_dir: Path):
        """Gera arquivo PDB com posições dos clusters"""
        pdb_path = output_dir / 'ftmap_enhanced_clusters.pdb'
        
        with open(pdb_path, 'w') as f:
            f.write("REMARK FTMap Enhanced - Top Clusters\n")
            f.write(f"REMARK Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("REMARK\n")
            
            for i, (_, cluster) in enumerate(top_clusters.iterrows(), 1):
                x, y, z = cluster['center_x'], cluster['center_y'], cluster['center_z']
                druggability = cluster['druggability_index']
                
                # Átomo fictício para representar o cluster
                f.write(f"HETATM{i:5d}  CA  HOT A{i:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00{druggability*100:6.2f}           C\n")
            
            f.write("END\n")
    
    def _generate_text_summary(self, report_data: ReportData, output_dir: Path):
        """Gera resumo em texto simples"""
        summary_path = output_dir / 'ftmap_enhanced_summary.txt'
        
        with open(summary_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("FTMap Enhanced - Resumo da Análise\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Proteína: {report_data.protein_name}\n")
            f.write(f"Data da análise: {report_data.metadata['analysis_date']}\n")
            f.write(f"Tempo de execução: {report_data.execution_time:.1f} segundos\n\n")
            
            f.write("ESTATÍSTICAS GERAIS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"• Total de poses: {report_data.total_poses:,}\n")
            f.write(f"• Clusters identificados: {report_data.total_clusters}\n")
            f.write(f"• Hotspots de alto potencial: {report_data.statistics['high_druggability_clusters']}\n")
            f.write(f"• Hotspots excepcionais: {report_data.statistics['exceptional_hotspots']}\n")
            f.write(f"• Druggability média: {report_data.statistics['mean_druggability']:.3f}\n\n")
            
            f.write("TOP 10 HOTSPOTS:\n")
            f.write("-" * 20 + "\n")
            for i, hotspot in enumerate(report_data.top_hotspots[:10], 1):
                f.write(f"{i:2d}. Cluster {hotspot['cluster_id']:3d} | ")
                f.write(f"Druggability: {hotspot['druggability_index']:.3f} | ")
                f.write(f"Energia: {hotspot['min_energy']:6.2f} kcal/mol | ")
                f.write(f"Tamanho: {hotspot['cluster_size']:3d} | ")
                f.write(f"Categoria: {hotspot['category']}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Arquivo gerado automaticamente pelo FTMap Enhanced\n")
    
    def _generate_executive_summary(self, report_data: ReportData, output_dir: Path) -> str:
        """Gera resumo executivo"""
        summary_path = output_dir / 'executive_summary.md'
        
        with open(summary_path, 'w') as f:
            f.write("# FTMap Enhanced - Resumo Executivo\n\n")
            
            f.write(f"**Proteína Analisada:** {report_data.protein_name}  \n")
            f.write(f"**Data da Análise:** {datetime.fromisoformat(report_data.metadata['analysis_date']).strftime('%d/%m/%Y %H:%M:%S')}  \n")
            f.write(f"**Tempo de Execução:** {report_data.execution_time:.1f} segundos  \n\n")
            
            f.write("## 📊 Principais Resultados\n\n")
            
            f.write(f"- **{report_data.total_poses:,} poses** foram geradas e analisadas\n")
            f.write(f"- **{report_data.total_clusters} clusters** foram identificados\n")
            f.write(f"- **{report_data.statistics['high_druggability_clusters']} hotspots** de alto potencial farmacológico\n")
            f.write(f"- **{report_data.statistics['exceptional_hotspots']} hotspots excepcionais** com características superiores\n")
            f.write(f"- **Druggability média:** {report_data.statistics['mean_druggability']:.3f}\n\n")
            
            if report_data.top_hotspots:
                best_hotspot = report_data.top_hotspots[0]
                f.write("## 🎯 Melhor Hotspot Identificado\n\n")
                f.write(f"**Cluster {best_hotspot['cluster_id']}** é o hotspot de maior potencial:\n")
                f.write(f"- Druggability Index: **{best_hotspot['druggability_index']:.3f}**\n")
                f.write(f"- Energia de Binding: **{best_hotspot['min_energy']:.2f} kcal/mol**\n")
                f.write(f"- Tamanho do Cluster: **{best_hotspot['cluster_size']} poses**\n")
                f.write(f"- Diversidade Química: **{best_hotspot['probe_diversity']} tipos de probe**\n")
                f.write(f"- Categoria: **{best_hotspot['category']}**\n\n")
            
            f.write("## 📈 Recomendações\n\n")
            
            high_potential = report_data.statistics['high_druggability_clusters']
            if high_potential >= 3:
                f.write("✅ **Excelente potencial farmacológico** - Múltiplos hotspots promissores identificados\n\n")
            elif high_potential >= 1:
                f.write("⚠️ **Potencial moderado** - Alguns hotspots promissores encontrados\n\n")
            else:
                f.write("❌ **Potencial limitado** - Poucos hotspots de alta qualidade identificados\n\n")
            
            f.write("Para análise detalhada consulte:\n")
            f.write("- `ftmap_enhanced_report.html` - Relatório visual completo\n")
            f.write("- `ftmap_enhanced_visualization.pml` - Script PyMOL para visualização 3D\n")
            f.write("- `ftmap_enhanced_features.csv` - Dados completos para análises customizadas\n")
        
        return str(summary_path)

# Função auxiliar para facilitar o uso
def generate_complete_analysis_report(features_df: pd.DataFrame,
                                    protein_info: Dict,
                                    docking_results: List[Dict],
                                    output_dir: str,
                                    config: VisualizationConfig = None) -> Dict[str, str]:
    """
    Função conveniente para gerar relatório completo
    
    Args:
        features_df: DataFrame com features dos clusters
        protein_info: Informações da proteína
        docking_results: Resultados do docking
        output_dir: Diretório de saída
        config: Configurações de visualização
    
    Returns:
        Dict com caminhos dos arquivos gerados
    """
    visualizer = VisualizationReports(config)
    return visualizer.generate_comprehensive_report(
        features_df, protein_info, docking_results, Path(output_dir)
    )
