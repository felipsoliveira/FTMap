#!/usr/bin/env python3
"""
FTMap Enhanced - Interface de Linha de Comando
Interface principal para execução do sistema FTMap Enhanced
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import logging

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent / "modules"))

from modules.workflow_manager import FTMapWorkflowManager
from modules.config import FTMapConfig


def setup_argument_parser():
    """Configura o parser de argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description="FTMap Enhanced - Sistema Modular para Análise de Druggability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

1. Análise completa básica:
   python ftmap_cli.py protein.pdb

2. Análise com configuração customizada:
   python ftmap_cli.py protein.pdb --config custom_config.json --output ./results

3. Análise pulando docking (usar resultados existentes):
   python ftmap_cli.py protein.pdb --skip-docking --output ./results

4. Resumir workflow interrompido:
   python ftmap_cli.py protein.pdb --resume workflow_state.json

5. Modo verbose com processamento paralelo:
   python ftmap_cli.py protein.pdb --verbose --processes 8

6. Análise rápida (configurações reduzidas):
   python ftmap_cli.py protein.pdb --quick-mode

Para mais informações: https://github.com/your-repo/ftmap-enhanced
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument(
        "protein_file",
        help="Arquivo da proteína (.pdb ou .pdbqt)"
    )
    
    # Argumentos opcionais - Configuração
    config_group = parser.add_argument_group("Configuração")
    config_group.add_argument(
        "--config", "-c",
        type=str,
        help="Arquivo de configuração JSON personalizada"
    )
    config_group.add_argument(
        "--output", "-o",
        type=str,
        help="Diretório de saída (padrão: ./ftmap_results)"
    )
    
    # Argumentos opcionais - Execução
    exec_group = parser.add_argument_group("Controle de Execução")
    exec_group.add_argument(
        "--skip-docking",
        action="store_true",
        help="Pular execução de docking (usar resultados existentes)"
    )
    exec_group.add_argument(
        "--resume",
        type=str,
        metavar="STATE_FILE",
        help="Resumir workflow a partir de arquivo de estado"
    )
    exec_group.add_argument(
        "--processes", "-p",
        type=int,
        default=4,
        help="Número de processos paralelos (padrão: 4)"
    )
    exec_group.add_argument(
        "--quick-mode",
        action="store_true",
        help="Modo rápido com configurações reduzidas"
    )
    
    # Argumentos opcionais - Filtering/Advanced
    advanced_group = parser.add_argument_group("Opções Avançadas")
    advanced_group.add_argument(
        "--energy-cutoff",
        type=float,
        help="Cutoff de energia para poses (kcal/mol)"
    )
    advanced_group.add_argument(
        "--min-cluster-size",
        type=int,
        help="Tamanho mínimo de cluster"
    )
    advanced_group.add_argument(
        "--max-clusters",
        type=int,
        help="Número máximo de clusters"
    )
    advanced_group.add_argument(
        "--probe-types",
        nargs="+",
        choices=["polar", "hydrophobic", "aromatic", "charged", "metal"],
        help="Tipos de probes a usar (padrão: todos)"
    )
    
    # Argumentos opcionais - Output
    output_group = parser.add_argument_group("Controle de Saída")
    output_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Saída verbose"
    )
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Saída mínima"
    )
    output_group.add_argument(
        "--no-reports",
        action="store_true",
        help="Não gerar relatórios HTML/visualizações"
    )
    output_group.add_argument(
        "--export-formats",
        nargs="+",
        choices=["json", "csv", "pdb", "sdf"],
        default=["json", "csv"],
        help="Formatos de exportação (padrão: json csv)"
    )
    
    # Argumentos opcionais - Workflow steps
    steps_group = parser.add_argument_group("Controle de Steps")
    steps_group.add_argument(
        "--steps",
        nargs="+",
        choices=["prep", "dock", "cluster", "features", "ml", "viz"],
        help="Executar apenas steps específicos"
    )
    steps_group.add_argument(
        "--start-from",
        choices=["prep", "dock", "cluster", "features", "ml", "viz"],
        help="Iniciar workflow a partir de step específico"
    )
    
    return parser


def load_custom_config(config_file: str) -> FTMapConfig:
    """Carrega configuração personalizada de arquivo JSON"""
    try:
        with open(config_file, 'r') as f:
            custom_settings = json.load(f)
        
        config = FTMapConfig()
        
        # Aplicar configurações personalizadas
        for key, value in custom_settings.items():
            if hasattr(config, key.upper()):
                setattr(config, key.upper(), value)
            else:
                print(f"⚠️  Configuração desconhecida ignorada: {key}")
        
        return config
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração {config_file}: {str(e)}")
        print("Usando configuração padrão...")
        return FTMapConfig()


def apply_cli_overrides(config: FTMapConfig, args: argparse.Namespace) -> FTMapConfig:
    """Aplica overrides da linha de comando na configuração"""
    
    if args.processes:
        config.PARALLEL_PROCESSES = args.processes
    
    if args.energy_cutoff:
        config.ENERGY_CUTOFF = args.energy_cutoff
    
    if args.min_cluster_size:
        config.MIN_CLUSTER_SIZE = args.min_cluster_size
    
    if args.max_clusters:
        config.MAX_CLUSTERS = args.max_clusters
    
    if args.probe_types:
        # Mapear tipos de probes
        probe_mapping = {
            "polar": ["water", "methanol", "ethanol"],
            "hydrophobic": ["butanol", "cyclohexane", "benzene"],
            "aromatic": ["benzene", "phenol", "indole"],
            "charged": ["acetate", "methylammonium"],
            "metal": ["zinc", "calcium"]
        }
        
        selected_probes = []
        for probe_type in args.probe_types:
            selected_probes.extend(probe_mapping.get(probe_type, []))
        
        if selected_probes:
            # Filtrar probe_molecules para manter apenas os selecionados
            filtered_probes = [probe for probe in config.probe_molecules if probe in selected_probes]
            config.probe_molecules = filtered_probes
    
    if args.quick_mode:
        # Configurações para modo rápido
        config.docking_config['num_modes'] = 5
        config.clustering_config['hierarchical']['n_clusters'] = 10
        config.analysis_thresholds['energy_cutoff'] = -4.0
        config.clustering_config['ensemble']['min_cluster_size'] = 3
        
        # Reduzir número de probes
        quick_probes = ["acetone", "benzene", "ethanol", "acetate"]
        config.probe_molecules = [probe for probe in config.probe_molecules if probe in quick_probes]
    
    return config


def setup_logging(verbose: bool, quiet: bool, output_dir: str):
    """Configura o sistema de logging"""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Handler para arquivo
    log_file = Path(output_dir) / "logs" / f"ftmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def validate_inputs(args: argparse.Namespace):
    """Valida argumentos de entrada"""
    # Verificar se arquivo de proteína existe
    if not Path(args.protein_file).exists():
        raise FileNotFoundError(f"Arquivo de proteína não encontrado: {args.protein_file}")
    
    # Verificar extensão do arquivo
    valid_extensions = ['.pdb', '.pdbqt']
    if not any(args.protein_file.lower().endswith(ext) for ext in valid_extensions):
        raise ValueError(f"Arquivo deve ter extensão {' ou '.join(valid_extensions)}")
    
    # Verificar arquivo de estado para resume
    if args.resume and not Path(args.resume).exists():
        raise FileNotFoundError(f"Arquivo de estado não encontrado: {args.resume}")
    
    # Verificar conflitos de argumentos
    if args.verbose and args.quiet:
        raise ValueError("Não é possível usar --verbose e --quiet simultaneamente")


def print_welcome_banner():
    """Imprime banner de boas-vindas"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           FTMap Enhanced v2.0                               ║
║                     Sistema Modular de Análise de Druggability              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🧬 Preparação de Proteínas    🎯 Docking Molecular                         ║
║  🎯 Análise de Clustering      🧠 Extração de Features                      ║
║  🤖 Machine Learning           📊 Visualizações & Relatórios                ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_results_summary(results: dict, output_dir: str):
    """Imprime resumo dos resultados"""
    summary = results.get('summary', {})
    metadata = results.get('workflow_metadata', {})
    
    print("\n" + "="*80)
    print("📊 RESUMO DOS RESULTADOS")
    print("="*80)
    
    # Estatísticas gerais
    if 'total_poses' in summary:
        print(f"🎯 Poses de docking: {summary['total_poses']} → {summary['filtered_poses']} (filtradas)")
    
    if 'clusters_found' in summary:
        print(f"🎯 Clusters encontrados: {summary['clusters_found']}")
    
    if 'features_extracted' in summary:
        print(f"🧠 Features extraídas: {summary['features_extracted']}")
    
    if 'predicted_druggable_sites' in summary:
        print(f"💊 Sítios druggable preditos: {summary['predicted_druggable_sites']}")
    
    if 'top_hotspot_score' in summary:
        print(f"🔥 Score do melhor hotspot: {summary['top_hotspot_score']:.3f}")
    
    # Informações de timing
    duration = metadata.get('total_duration', 0)
    print(f"⏱️  Tempo total: {duration:.1f}s ({duration/60:.1f} min)")
    
    # Informações de output
    print(f"📁 Resultados salvos em: {output_dir}")
    
    # Arquivos principais
    report_file = Path(output_dir) / "reports" / "*.html"
    print(f"📄 Relatório HTML: {report_file}")
    
    print("="*80)


def main():
    """Função principal da CLI"""
    try:
        # Parse argumentos
        parser = setup_argument_parser()
        args = parser.parse_args()
        
        # Mostrar banner se não estiver em modo quiet
        if not args.quiet:
            print_welcome_banner()
        
        # Validar argumentos
        validate_inputs(args)
        
        # Configurar output directory
        output_dir = args.output or f"./ftmap_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Configurar logging
        setup_logging(args.verbose, args.quiet, output_dir)
        logger = logging.getLogger('FTMapCLI')
        
        logger.info(f"🚀 Iniciando FTMap Enhanced")
        logger.info(f"📁 Proteína: {args.protein_file}")
        logger.info(f"📁 Output: {output_dir}")
        
        # Carregar configuração
        if args.config:
            logger.info(f"📄 Carregando configuração: {args.config}")
            config = load_custom_config(args.config)
        else:
            config = FTMapConfig()
        
        # Aplicar overrides da CLI
        config = apply_cli_overrides(config, args)
        
        # Inicializar workflow manager
        workflow = FTMapWorkflowManager(config=config, output_dir=output_dir)
        
        # Executar workflow
        if args.resume:
            logger.info(f"📤 Resumindo workflow: {args.resume}")
            results = workflow.resume_workflow(args.resume, args.protein_file)
        else:
            logger.info("⚡ Executando workflow completo")
            results = workflow.run_complete_workflow(
                protein_file=args.protein_file,
                skip_docking=args.skip_docking,
                resume_from_step=args.start_from
            )
        
        # Mostrar resumo se não estiver em modo quiet
        if not args.quiet:
            print_results_summary(results, output_dir)
        
        # Success
        logger.info("✅ Workflow concluído com sucesso!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido pelo usuário")
        return 1
        
    except Exception as e:
        logger.error(f"💥 Erro crítico: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
