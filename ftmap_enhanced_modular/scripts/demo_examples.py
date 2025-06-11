#!/usr/bin/env python3
"""
FTMap Enhanced - Script de Demonstração
Exemplos práticos de uso do sistema FTMap Enhanced
"""

import os
import sys
import time
from pathlib import Path

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent / "modules"))

from modules.workflow_manager import FTMapWorkflowManager
from configs.config import FTMapConfig


def demo_basic_analysis():
    """Demonstração: Análise básica completa"""
    print("🧪 DEMO 1: Análise Básica Completa")
    print("="*50)
    
    # Proteína de exemplo (você pode baixar de PDB)
    protein_file = "example_protein.pdb"  # Substitua por arquivo real
    
    if not Path(protein_file).exists():
        print(f"❌ Arquivo {protein_file} não encontrado")
        print("💡 Baixe uma proteína exemplo do PDB:")
        print("   wget https://files.rcsb.org/download/1ABC.pdb -O example_protein.pdb")
        return
    
    # Configuração padrão
    config = FTMapConfig()
    
    # Inicializar workflow
    workflow = FTMapWorkflowManager(
        config=config,
        output_dir="./demo1_basic_analysis"
    )
    
    # Executar análise completa
    print("🚀 Executando análise completa...")
    start_time = time.time()
    
    try:
        results = workflow.run_complete_workflow(protein_file)
        
        duration = time.time() - start_time
        print(f"✅ Análise concluída em {duration:.1f}s")
        print(f"📊 {results['summary']['clusters_found']} clusters encontrados")
        print(f"💊 {results['summary']['predicted_druggable_sites']} sítios druggable")
        print(f"📁 Resultados em: ./demo1_basic_analysis")
        
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")


def demo_custom_configuration():
    """Demonstração: Configuração personalizada"""
    print("\n🧪 DEMO 2: Configuração Personalizada")
    print("="*50)
    
    protein_file = "example_protein.pdb"
    
    if not Path(protein_file).exists():
        print(f"❌ Arquivo {protein_file} não encontrado")
        return
    
    # Configuração personalizada
    config = FTMapConfig()
    
    # Modificar parâmetros para análise rápida
    config.TARGET_POSES_PER_PROBE = 5  # Reduzir poses
    config.ENERGY_CUTOFF = -3.0        # Menos restritivo
    config.MAX_CLUSTERS = 8            # Menos clusters
    config.PARALLEL_PROCESSES = 8      # Mais paralelização
    
    # Usar apenas probes específicos
    quick_probes = ["water", "methanol", "benzene", "acetate"]
    config.PROBE_MOLECULES = {k: v for k, v in config.PROBE_MOLECULES.items() 
                            if k in quick_probes}
    
    print(f"🎯 Usando {len(config.PROBE_MOLECULES)} probes")
    print(f"⚡ {config.PARALLEL_PROCESSES} processos paralelos")
    
    # Inicializar workflow
    workflow = FTMapWorkflowManager(
        config=config,
        output_dir="./demo2_custom_config"
    )
    
    # Executar análise
    print("🚀 Executando análise personalizada...")
    start_time = time.time()
    
    try:
        results = workflow.run_complete_workflow(protein_file)
        
        duration = time.time() - start_time
        print(f"✅ Análise rápida concluída em {duration:.1f}s")
        print(f"📊 Resultados em: ./demo2_custom_config")
        
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")


def demo_step_by_step():
    """Demonstração: Execução step-by-step"""
    print("\n🧪 DEMO 3: Execução Step-by-Step")
    print("="*50)
    
    protein_file = "example_protein.pdb"
    
    if not Path(protein_file).exists():
        print(f"❌ Arquivo {protein_file} não encontrado")
        return
    
    config = FTMapConfig()
    workflow = FTMapWorkflowManager(
        config=config,
        output_dir="./demo3_step_by_step"
    )
    
    print("🧬 Step 1: Preparação da proteína...")
    try:
        # Step 1: Preparação
        prep_result = workflow._step_protein_preparation(protein_file, {})
        print(f"   ✅ {len(prep_result['binding_sites'])} sítios de ligação detectados")
        
        # Step 2: Docking (apenas alguns probes para demo)
        print("🎯 Step 2: Docking molecular...")
        mock_previous = {'protein_preparation': prep_result}
        dock_result = workflow._step_docking_execution(protein_file, mock_previous)
        print(f"   ✅ {dock_result['filtered_poses']} poses filtradas")
        
        # Step 3: Clustering
        print("🎯 Step 3: Análise de clustering...")
        mock_previous['docking_execution'] = dock_result
        cluster_result = workflow._step_clustering_analysis(protein_file, mock_previous)
        print(f"   ✅ {len(cluster_result['final_clusters'])} clusters formados")
        
        print("🎉 Demo step-by-step concluída!")
        
    except Exception as e:
        print(f"❌ Erro no step-by-step: {str(e)}")


def demo_visualization_only():
    """Demonstração: Apenas visualizações de resultados existentes"""
    print("\n🧪 DEMO 4: Visualizações de Resultados Existentes")
    print("="*50)
    
    # Verificar se existem resultados anteriores
    results_dirs = [d for d in Path(".").iterdir() 
                   if d.is_dir() and d.name.startswith("demo")]
    
    if not results_dirs:
        print("❌ Nenhum resultado anterior encontrado")
        print("💡 Execute primeiro uma das outras demos")
        return
    
    # Usar o primeiro diretório encontrado
    results_dir = results_dirs[0]
    print(f"📁 Usando resultados de: {results_dir}")
    
    # Procurar por arquivos de estado
    state_files = list(results_dir.glob("workflow_state.json"))
    
    if not state_files:
        print("❌ Arquivo de estado não encontrado")
        return
    
    state_file = state_files[0]
    
    try:
        import json
        with open(state_file, 'r') as f:
            saved_results = json.load(f)
        
        print("📊 Gerando visualizações adicionais...")
        
        # Aqui você poderia implementar visualizações específicas
        # Por exemplo, plots personalizados, análises comparativas, etc.
        
        print("✅ Visualizações geradas!")
        print(f"📁 Verifique: {results_dir}/visualizations/")
        
    except Exception as e:
        print(f"❌ Erro na visualização: {str(e)}")


def demo_comparison_analysis():
    """Demonstração: Análise comparativa de múltiplas proteínas"""
    print("\n🧪 DEMO 5: Análise Comparativa")
    print("="*50)
    
    # Lista de proteínas para comparar
    proteins = ["protein1.pdb", "protein2.pdb"]  # Substitua por arquivos reais
    
    available_proteins = [p for p in proteins if Path(p).exists()]
    
    if len(available_proteins) < 2:
        print("❌ Necessário pelo menos 2 proteínas para comparação")
        print("💡 Disponibilize arquivos: protein1.pdb, protein2.pdb")
        return
    
    print(f"🔬 Comparando {len(available_proteins)} proteínas...")
    
    results = {}
    config = FTMapConfig()
    
    for i, protein in enumerate(available_proteins):
        print(f"\n📊 Analisando proteína {i+1}: {protein}")
        
        workflow = FTMapWorkflowManager(
            config=config,
            output_dir=f"./demo5_comparison/protein_{i+1}"
        )
        
        try:
            result = workflow.run_complete_workflow(protein)
            results[protein] = result['summary']
            print(f"   ✅ {result['summary']['clusters_found']} clusters")
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    # Comparar resultados
    if len(results) >= 2:
        print("\n📈 COMPARAÇÃO DE RESULTADOS:")
        print("-" * 40)
        
        for protein, summary in results.items():
            print(f"{protein}:")
            print(f"  Clusters: {summary.get('clusters_found', 0)}")
            print(f"  Sítios druggable: {summary.get('predicted_druggable_sites', 0)}")
            print(f"  Top score: {summary.get('top_hotspot_score', 0):.3f}")


def demo_performance_benchmark():
    """Demonstração: Benchmark de performance"""
    print("\n🧪 DEMO 6: Benchmark de Performance")
    print("="*50)
    
    protein_file = "example_protein.pdb"
    
    if not Path(protein_file).exists():
        print(f"❌ Arquivo {protein_file} não encontrado")
        return
    
    # Testar diferentes configurações de paralelização
    parallel_configs = [1, 2, 4, 8]
    results = {}
    
    for processes in parallel_configs:
        print(f"\n⚡ Testando com {processes} processo(s)...")
        
        config = FTMapConfig()
        config.PARALLEL_PROCESSES = processes
        config.TARGET_POSES_PER_PROBE = 3  # Reduzir para benchmark
        
        # Usar apenas probes essenciais
        config.PROBE_MOLECULES = {k: v for k, v in config.PROBE_MOLECULES.items() 
                                if k in ["water", "methanol", "benzene"]}
        
        workflow = FTMapWorkflowManager(
            config=config,
            output_dir=f"./demo6_benchmark/test_{processes}proc"
        )
        
        start_time = time.time()
        
        try:
            workflow_result = workflow.run_complete_workflow(protein_file)
            duration = time.time() - start_time
            
            results[processes] = {
                'duration': duration,
                'clusters': workflow_result['summary']['clusters_found']
            }
            
            print(f"   ✅ Concluído em {duration:.1f}s")
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            results[processes] = {'duration': None, 'error': str(e)}
    
    # Mostrar resultados do benchmark
    print("\n📊 RESULTADOS DO BENCHMARK:")
    print("-" * 40)
    
    for processes, result in results.items():
        if result['duration']:
            speedup = results[1]['duration'] / result['duration'] if 1 in results and results[1]['duration'] else 1
            print(f"{processes} processo(s): {result['duration']:.1f}s (speedup: {speedup:.1f}x)")
        else:
            print(f"{processes} processo(s): ERRO")


def main():
    """Menu principal das demonstrações"""
    print("🧪 FTMap Enhanced - Demonstrações")
    print("="*50)
    
    demos = [
        ("Análise Básica Completa", demo_basic_analysis),
        ("Configuração Personalizada", demo_custom_configuration), 
        ("Execução Step-by-Step", demo_step_by_step),
        ("Visualizações Existentes", demo_visualization_only),
        ("Análise Comparativa", demo_comparison_analysis),
        ("Benchmark de Performance", demo_performance_benchmark)
    ]
    
    print("\nDemonstrações disponíveis:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    
    print("\nDigite o número da demo (ou 'all' para todas):")
    choice = input("> ").strip()
    
    if choice.lower() == 'all':
        print("\n🚀 Executando todas as demonstrações...")
        for name, demo_func in demos:
            print(f"\n{'='*60}")
            print(f"Executando: {name}")
            print(f"{'='*60}")
            try:
                demo_func()
            except Exception as e:
                print(f"❌ Erro na demo {name}: {str(e)}")
    
    elif choice.isdigit() and 1 <= int(choice) <= len(demos):
        demo_index = int(choice) - 1
        name, demo_func = demos[demo_index]
        
        print(f"\n🚀 Executando: {name}")
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Erro na demo: {str(e)}")
    
    else:
        print("❌ Opção inválida")


if __name__ == "__main__":
    main()
