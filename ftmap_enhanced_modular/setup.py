#!/usr/bin/env python3
"""
FTMap Enhanced - Setup e Instalação
Script para configurar ambiente e dependências
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import requests
import json


def print_header():
    """Imprime cabeçalho do setup"""
    print("🛠️  FTMap Enhanced - Setup e Instalação")
    print("="*50)
    print(f"🖥️  Sistema: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()


def check_python_version():
    """Verifica versão do Python"""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    print("🔍 Verificando versão do Python...")
    
    if current_version >= min_version:
        print(f"✅ Python {sys.version.split()[0]} OK")
        return True
    else:
        print(f"❌ Python {min_version[0]}.{min_version[1]}+ necessário")
        print(f"   Versão atual: {current_version[0]}.{current_version[1]}")
        return False


def install_pip_dependencies():
    """Instala dependências Python"""
    print("\n📦 Instalando dependências Python...")
    
    dependencies = [
        "numpy>=1.21.0",
        "scipy>=1.7.0", 
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "biopython>=1.79",
        "rdkit-pypi>=2022.3.0",
        "openmm>=7.6.0",
        "mdanalysis>=2.0.0",
        "pymol-open-source>=2.5.0",
        "joblib>=1.1.0",
        "tqdm>=4.62.0",
        "requests>=2.26.0",
        "jinja2>=3.0.0"
    ]
    
    failed_packages = []
    
    for package in dependencies:
        try:
            print(f"  📥 Instalando {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"     ✅ {package} instalado")
            else:
                print(f"     ❌ Erro ao instalar {package}")
                failed_packages.append(package)
                
        except subprocess.TimeoutExpired:
            print(f"     ⏰ Timeout ao instalar {package}")
            failed_packages.append(package)
        except Exception as e:
            print(f"     ❌ Erro inesperado: {str(e)}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Pacotes com falha na instalação:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 Tente instalar manualmente:")
        print(f"   pip install {' '.join(failed_packages)}")
        return False
    else:
        print("\n✅ Todas as dependências Python instaladas!")
        return True


def check_external_tools():
    """Verifica ferramentas externas necessárias"""
    print("\n🔧 Verificando ferramentas externas...")
    
    tools = {
        "AutoDock Vina": {
            "command": "vina",
            "install_hint": "Baixe de: http://vina.scripps.edu/",
            "required": True
        },
        "Open Babel": {
            "command": "obabel",
            "install_hint": "conda install -c conda-forge openbabel",
            "required": True
        },
        "PyMOL": {
            "command": "pymol",
            "install_hint": "conda install -c conda-forge pymol-open-source",
            "required": False
        },
        "GROMACS": {
            "command": "gmx",
            "install_hint": "conda install -c conda-forge gromacs",
            "required": False
        }
    }
    
    missing_required = []
    missing_optional = []
    
    for tool_name, info in tools.items():
        try:
            result = subprocess.run([info["command"], "--help"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"  ✅ {tool_name} encontrado")
            else:
                raise subprocess.CalledProcessError(1, info["command"])
                
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"  ❌ {tool_name} não encontrado")
            print(f"     💡 {info['install_hint']}")
            
            if info["required"]:
                missing_required.append(tool_name)
            else:
                missing_optional.append(tool_name)
    
    if missing_required:
        print(f"\n⚠️  Ferramentas obrigatórias ausentes: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n💡 Ferramentas opcionais ausentes: {', '.join(missing_optional)}")
        print("   Sistema funcionará com funcionalidade reduzida")
    
    return True


def setup_directories():
    """Configura estrutura de diretórios"""
    print("\n📁 Configurando estrutura de diretórios...")
    
    base_dir = Path(__file__).parent.parent
    
    directories = [
        "data/input",
        "data/output", 
        "data/temp",
        "data/examples",
        "logs",
        "tests/unit",
        "tests/integration",
        "docs/api",
        "docs/tutorials"
    ]
    
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  📂 {dir_path}")
    
    print("✅ Estrutura de diretórios criada")


def download_example_files():
    """Baixa arquivos de exemplo"""
    print("\n📥 Baixando arquivos de exemplo...")
    
    examples_dir = Path(__file__).parent.parent / "data" / "examples"
    
    # URLs de proteínas exemplo do PDB
    example_proteins = [
        {
            "name": "1abc.pdb",
            "url": "https://files.rcsb.org/download/1ABC.pdb",
            "description": "Proteína exemplo pequena"
        },
        {
            "name": "2xyz.pdb", 
            "url": "https://files.rcsb.org/download/2XYZ.pdb",
            "description": "Proteína exemplo média"
        }
    ]
    
    downloaded = []
    
    for protein in example_proteins:
        file_path = examples_dir / protein["name"]
        
        if file_path.exists():
            print(f"  ✅ {protein['name']} já existe")
            continue
        
        try:
            print(f"  📥 Baixando {protein['name']}...")
            response = requests.get(protein["url"], timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'w') as f:
                f.write(response.text)
            
            print(f"     ✅ {protein['description']}")
            downloaded.append(protein["name"])
            
        except requests.RequestException as e:
            print(f"     ❌ Erro ao baixar {protein['name']}: {str(e)}")
        except Exception as e:
            print(f"     ❌ Erro inesperado: {str(e)}")
    
    if downloaded:
        print(f"\n✅ {len(downloaded)} arquivo(s) de exemplo baixado(s)")
    
    return len(downloaded) > 0


def create_config_file():
    """Cria arquivo de configuração personalizada"""
    print("\n⚙️  Criando arquivo de configuração...")
    
    config_dir = Path(__file__).parent.parent / "configs"
    config_file = config_dir / "user_config.json"
    
    if config_file.exists():
        print("  ✅ Configuração já existe")
        return True
    
    # Configuração padrão para usuário
    user_config = {
        "parallel_processes": 4,
        "energy_cutoff": -5.0,
        "target_poses_per_probe": 10,
        "max_clusters": 15,
        "min_cluster_size": 5,
        "clustering_eps": 2.0,
        "output_formats": ["json", "csv", "html"],
        "enable_visualization": True,
        "verbose_output": False,
        "probe_molecules": {
            "water": {"smiles": "O", "charge": 0},
            "methanol": {"smiles": "CO", "charge": 0},
            "ethanol": {"smiles": "CCO", "charge": 0},
            "benzene": {"smiles": "c1ccccc1", "charge": 0},
            "acetate": {"smiles": "CC(=O)[O-]", "charge": -1}
        }
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(user_config, f, indent=2)
        
        print(f"  ✅ Configuração criada: {config_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao criar configuração: {str(e)}")
        return False


def create_test_suite():
    """Cria suite básica de testes"""
    print("\n🧪 Configurando suite de testes...")
    
    tests_dir = Path(__file__).parent.parent / "tests"
    
    # Teste unitário básico
    unit_test = '''#!/usr/bin/env python3
"""
Testes unitários básicos para FTMap Enhanced
"""

import unittest
import sys
from pathlib import Path

# Adicionar path dos módulos
sys.path.append(str(Path(__file__).parent.parent / "modules"))

from config import FTMapConfig


class TestConfig(unittest.TestCase):
    """Testes para configuração"""
    
    def test_config_creation(self):
        """Testa criação da configuração"""
        config = FTMapConfig()
        self.assertIsNotNone(config)
        self.assertGreater(len(config.PROBE_MOLECULES), 0)
    
    def test_config_values(self):
        """Testa valores padrão da configuração"""
        config = FTMapConfig()
        self.assertGreater(config.PARALLEL_PROCESSES, 0)
        self.assertLess(config.ENERGY_CUTOFF, 0)


if __name__ == "__main__":
    unittest.main()
'''
    
    unit_test_file = tests_dir / "unit" / "test_config.py"
    
    try:
        with open(unit_test_file, 'w') as f:
            f.write(unit_test)
        
        print("  ✅ Teste unitário criado")
        
        # Tentar executar teste
        result = subprocess.run([
            sys.executable, str(unit_test_file)
        ], capture_output=True, text=True, cwd=tests_dir.parent)
        
        if result.returncode == 0:
            print("  ✅ Teste executado com sucesso")
        else:
            print("  ⚠️  Teste falhou - verifique configuração")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao criar testes: {str(e)}")
        return False


def create_launcher_scripts():
    """Cria scripts de lançamento convenientes"""
    print("\n🚀 Criando scripts de lançamento...")
    
    base_dir = Path(__file__).parent.parent
    
    # Script para Linux/Mac
    bash_script = f'''#!/bin/bash
# FTMap Enhanced Launcher

SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

python3 ftmap_cli.py "$@"
'''
    
    # Script para Windows
    batch_script = f'''@echo off
REM FTMap Enhanced Launcher

cd /d "%~dp0"
python ftmap_cli.py %*
'''
    
    try:
        # Criar script bash
        bash_file = base_dir / "ftmap.sh"
        with open(bash_file, 'w') as f:
            f.write(bash_script)
        bash_file.chmod(0o755)
        
        # Criar script batch  
        batch_file = base_dir / "ftmap.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_script)
        
        print("  ✅ Scripts de lançamento criados")
        print(f"     🐧 Linux/Mac: ./ftmap.sh")
        print(f"     🪟 Windows: ftmap.bat")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao criar scripts: {str(e)}")
        return False


def run_verification_test():
    """Executa teste de verificação do sistema"""
    print("\n🔍 Executando teste de verificação...")
    
    try:
        # Importar módulos principais
        sys.path.append(str(Path(__file__).parent / "modules"))
        
        print("  🧪 Testando imports...")
        from config import FTMapConfig
        from workflow_manager import FTMapWorkflowManager
        
        print("  ✅ Imports OK")
        
        # Testar inicialização
        print("  🧪 Testando inicialização...")
        config = FTMapConfig()
        workflow = FTMapWorkflowManager(config=config, output_dir="/tmp/ftmap_test")
        
        print("  ✅ Inicialização OK")
        
        # Verificar status
        status = workflow.get_workflow_status()
        print(f"  ✅ Status: {status['output_directory']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na verificação: {str(e)}")
        return False


def main():
    """Função principal do setup"""
    print_header()
    
    # Verificações e instalações
    checks = [
        ("Versão do Python", check_python_version),
        ("Dependências Python", install_pip_dependencies),
        ("Ferramentas Externas", check_external_tools),
        ("Estrutura de Diretórios", setup_directories),
        ("Arquivos de Exemplo", download_example_files),
        ("Arquivo de Configuração", create_config_file),
        ("Suite de Testes", create_test_suite),
        ("Scripts de Lançamento", create_launcher_scripts),
        ("Verificação Final", run_verification_test)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{'='*50}")
        print(f"🔧 {name}")
        print(f"{'='*50}")
        
        try:
            success = check_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Erro inesperado em {name}: {str(e)}")
            results.append((name, False))
    
    # Resumo final
    print(f"\n{'='*50}")
    print("📊 RESUMO DA INSTALAÇÃO")
    print(f"{'='*50}")
    
    successful = 0
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if success:
            successful += 1
    
    print(f"\n📈 {successful}/{len(results)} verificações bem-sucedidas")
    
    if successful == len(results):
        print("\n🎉 Setup concluído com sucesso!")
        print("\n🚀 Para começar:")
        print("   ./ftmap.sh example_protein.pdb")
        print("   ou")
        print("   python ftmap_cli.py example_protein.pdb")
    else:
        print("\n⚠️  Setup concluído com problemas")
        print("💡 Revise os erros acima antes de usar o sistema")
    
    print(f"\n📚 Documentação e exemplos em:")
    print(f"   📁 {Path(__file__).parent.parent}")


if __name__ == "__main__":
    main()
