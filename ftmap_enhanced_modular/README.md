# FTMap Enhanced - Sistema Modular de Análise de Druggability

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0-green.svg)](https://github.com/your-repo/ftmap-enhanced)

## 🎯 Visão Geral

O **FTMap Enhanced** é um sistema modular avançado para análise de druggability proteica, baseado no algoritmo FTMap original mas completamente reformulado com arquitetura modular, machine learning integrado e capacidades de análise avançada.

### 🌟 Características Principais

- **🧬 Preparação Inteligente de Proteínas**: Limpeza, análise de estrutura e detecção automática de cavidades
- **🎯 Docking Molecular Paralelo**: Execução eficiente com múltiplos probes farmacofóricos
- **🎯 Análise de Clustering Avançada**: Algoritmos ensemble (DBSCAN, hierárquico, consensus)
- **🧠 Extração de Features Multidimensional**: 25+ features energéticas, espaciais, químicas e farmacofóricas
- **🤖 Machine Learning Integrado**: Modelos ensemble para predição de druggability e scoring
- **📊 Visualizações Interativas**: Relatórios HTML, scripts PyMOL e plots estatísticos
- **⚡ Processamento Paralelo**: Otimizado para máxima performance
- **🔧 Configuração Flexível**: Sistema de configuração centralizado e personalizável

## 🏗️ Arquitetura Modular

```
ftmap_enhanced_modular/
├── configs/                    # Configurações
│   ├── config.py              # Configuração principal
│   └── user_config.json       # Configuração personalizada
├── modules/                    # Módulos principais
│   ├── protein_preparation.py # Preparação de proteínas
│   ├── molecular_docking.py   # Docking molecular
│   ├── clustering_analysis.py # Análise de clustering
│   ├── feature_extraction.py  # Extração de features
│   ├── machine_learning.py    # Predições ML
│   ├── visualization_reports.py # Visualizações
│   └── workflow_manager.py    # Orquestrador principal
├── scripts/                   # Scripts utilitários
│   └── demo_examples.py       # Exemplos e demos
├── data/                      # Dados
│   ├── input/                 # Proteínas de entrada
│   ├── output/                # Resultados
│   ├── temp/                  # Arquivos temporários
│   └── examples/              # Arquivos exemplo
├── tests/                     # Testes
│   ├── unit/                  # Testes unitários
│   └── integration/           # Testes de integração
├── docs/                      # Documentação
├── ftmap_cli.py              # Interface de linha de comando
└── setup.py                  # Script de instalação
```

## 🚀 Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/your-repo/ftmap-enhanced.git
cd ftmap-enhanced
```

### 2. Execute o Setup Automático
```bash
python setup.py
```

O script de setup irá:
- ✅ Verificar dependências Python
- 📦 Instalar pacotes necessários
- 🔧 Verificar ferramentas externas
- 📁 Configurar estrutura de diretórios
- 📥 Baixar arquivos de exemplo
- 🧪 Executar testes de verificação

### 3. Dependências Externas

**Obrigatórias:**
- [AutoDock Vina](http://vina.scripps.edu/) - Para docking molecular
- [Open Babel](https://openbabel.org/) - Conversão de formatos

**Opcionais:**
- [PyMOL](https://pymol.org/) - Visualização molecular
- [GROMACS](http://www.gromacs.org/) - Simulações MD

```bash
# Instalação via conda (recomendado)
conda install -c conda-forge openbabel pymol-open-source gromacs

# AutoDock Vina - baixar do site oficial
```

## 💻 Uso Básico

### Interface de Linha de Comando

```bash
# Análise completa básica
python ftmap_cli.py protein.pdb

# Análise com configurações personalizadas
python ftmap_cli.py protein.pdb --config custom_config.json --output ./results

# Análise rápida (modo otimizado)
python ftmap_cli.py protein.pdb --quick-mode --processes 8

# Pular docking (usar resultados existentes)
python ftmap_cli.py protein.pdb --skip-docking

# Resumir workflow interrompido
python ftmap_cli.py protein.pdb --resume workflow_state.json
```

### Scripts de Lançamento

```bash
# Linux/Mac
./ftmap.sh protein.pdb

# Windows
ftmap.bat protein.pdb
```

### Uso Programático

```python
from modules.workflow_manager import FTMapWorkflowManager
from configs.config import FTMapConfig

# Configuração personalizada
config = FTMapConfig()
config.PARALLEL_PROCESSES = 8
config.ENERGY_CUTOFF = -5.0

# Inicializar workflow
workflow = FTMapWorkflowManager(
    config=config,
    output_dir="./my_results"
)

# Executar análise completa
results = workflow.run_complete_workflow("protein.pdb")

# Resultados
print(f"Clusters encontrados: {results['summary']['clusters_found']}")
print(f"Sítios druggable: {results['summary']['predicted_druggable_sites']}")
```

## 📊 Exemplos e Demonstrações

Execute o script de demonstrações para ver o sistema em ação:

```bash
python scripts/demo_examples.py
```

**Demos disponíveis:**
1. 🧪 **Análise Básica Completa** - Workflow completo com configuração padrão
2. ⚙️  **Configuração Personalizada** - Como customizar parâmetros
3. 🔄 **Execução Step-by-Step** - Controle granular do pipeline
4. 📊 **Visualizações Existentes** - Gerar plots de resultados salvos
5. 🔬 **Análise Comparativa** - Comparar múltiplas proteínas
6. ⚡ **Benchmark de Performance** - Otimização de paralelização

## 🎯 Fluxo de Trabalho

### 1. Preparação da Proteína
- Limpeza e validação da estrutura
- Detecção automática de cavidades/sítios de ligação
- Cálculo de propriedades geométricas
- Conversão para formato PDBQT

### 2. Docking Molecular
- Biblioteca de probes farmacofóricos (água, metanol, benzeno, etc.)
- Execução paralela de docking com AutoDock Vina
- Filtragem por energia e qualidade
- Otimização de poses

### 3. Análise de Clustering
- **DBSCAN**: Clustering baseado em densidade
- **Hierárquico**: Clustering aglomerativo
- **Ensemble**: Consenso entre métodos
- Métricas de qualidade (silhouette, Davies-Bouldin)

### 4. Extração de Features
- **Energéticas**: Scores de binding, distribuições energéticas
- **Espaciais**: Centros de massa, volumes, distâncias
- **Químicas**: Tipos de átomos, propriedades moleculares
- **Farmacofóricas**: Padrões de interação, pontos funcionais
- **Densidade**: Ocupação espacial, compactação
- **Estatísticas**: Médias, desvios, correlações

### 5. Machine Learning
- **Random Forest**: Classificação robusta
- **Gradient Boosting**: Predições refinadas
- **Neural Networks**: Padrões complexos
- **Ensemble**: Combinação de modelos
- Predição de druggability, scoring de hotspots

### 6. Visualização e Relatórios
- **Relatório HTML**: Dashboard interativo completo
- **Scripts PyMOL**: Visualização 3D profissional
- **Plots Estatísticos**: Análises gráficas detalhadas
- **Exportação**: JSON, CSV, PDB, SDF

## ⚙️ Configuração

### Arquivo de Configuração Principal

```python
# configs/config.py
class FTMapConfig:
    # Docking
    PARALLEL_PROCESSES = 4
    TARGET_POSES_PER_PROBE = 10
    ENERGY_CUTOFF = -5.0
    
    # Clustering
    CLUSTERING_EPS = 2.0
    MIN_CLUSTER_SIZE = 5
    MAX_CLUSTERS = 15
    
    # Machine Learning
    ML_TRAIN_TEST_SPLIT = 0.3
    ML_CV_FOLDS = 5
    
    # Probes
    PROBE_MOLECULES = {
        "water": {"smiles": "O", "charge": 0},
        "methanol": {"smiles": "CO", "charge": 0},
        # ...mais probes
    }
```

### Configuração Personalizada

```json
// configs/user_config.json
{
    "parallel_processes": 8,
    "energy_cutoff": -6.0,
    "quick_mode": true,
    "probe_molecules": {
        "water": {"smiles": "O", "charge": 0},
        "benzene": {"smiles": "c1ccccc1", "charge": 0}
    }
}
```

## 📈 Resultados e Saídas

### Estrutura de Resultados

```
ftmap_results/
├── prepared_proteins/          # Proteínas processadas
│   ├── protein_prepared.pdbqt
│   └── protein_metadata.json
├── docking_results/           # Resultados de docking
│   └── protein_docking.json
├── clusters/                  # Análise de clustering
│   └── protein_clusters.json
├── features/                  # Features extraídas
│   └── protein_features.json
├── models/                    # Modelos ML
│   ├── protein_predictions.json
│   └── trained_models/
├── reports/                   # Relatórios finais
│   ├── protein_report.html
│   └── protein_export.csv
├── visualizations/           # Visualizações
│   ├── protein_visualization.pml
│   └── plots/
├── logs/                     # Logs de execução
└── workflow_state.json      # Estado do workflow
```

### Métricas de Qualidade

- **Druggability Score**: 0.0 - 1.0 (probabilidade de ser druggable)
- **Hotspot Score**: 0.0 - 1.0 (intensidade do hotspot)
- **Binding Affinity**: Predição de afinidade de ligação
- **Confidence Score**: Confiabilidade da predição
- **Cluster Quality**: Métricas de silhouette e compactação

## 🧪 Testes

### Executar Testes

```bash
# Testes unitários
python -m unittest tests/unit/test_*.py

# Testes de integração
python -m unittest tests/integration/test_*.py

# Todos os testes
python -m unittest discover tests/
```

### Testes de Performance

```bash
# Benchmark de paralelização
python scripts/demo_examples.py
# Selecionar opção 6: Benchmark de Performance
```

## 🔧 Solução de Problemas

### Problemas Comuns

**1. Erro de dependências Python**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**2. AutoDock Vina não encontrado**
```bash
# Adicionar Vina ao PATH ou especificar caminho completo
export PATH="/path/to/vina:$PATH"
```

**3. Memória insuficiente**
```bash
# Reduzir paralelização
python ftmap_cli.py protein.pdb --processes 2 --quick-mode
```

**4. Timeout no docking**
```bash
# Aumentar timeout ou reduzir número de poses
python ftmap_cli.py protein.pdb --energy-cutoff -4.0
```

### Logs e Debugging

```bash
# Modo verbose
python ftmap_cli.py protein.pdb --verbose

# Verificar logs
tail -f ftmap_results/logs/ftmap_*.log
```

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/nova-feature`)
5. **Abra** um Pull Request

### Diretrizes de Desenvolvimento

- Seguir PEP 8 para estilo de código
- Adicionar testes para novas funcionalidades
- Documentar APIs e módulos
- Manter compatibilidade backwards

### Reportar Bugs

Use o [sistema de issues](https://github.com/your-repo/ftmap-enhanced/issues) com:
- Descrição clara do problema
- Passos para reproduzir
- Versão do Python e sistema operacional
- Logs relevantes

## 📚 Documentação Adicional

### Tutoriais
- [Tutorial Básico](docs/tutorials/basic_tutorial.md)
- [Configurações Avançadas](docs/tutorials/advanced_config.md)
- [Customização de Probes](docs/tutorials/custom_probes.md)
- [Integração com Pipelines](docs/tutorials/pipeline_integration.md)

### API Reference
- [Documentação da API](docs/api/)
- [Exemplos de Código](docs/examples/)

### Artigos Científicos
- FTMap Original: [Kozakov et al., Nature Protocols, 2015](https://doi.org/10.1038/nprot.2015.043)
- Metodologia de Clustering: [Rodriguez & Laio, Science, 2014](https://doi.org/10.1126/science.1242072)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **FTMap Original**: Dima Kozakov e equipe (Stony Brook University)
- **AutoDock Vina**: Oleg Trott e Arthur Olson (Scripps Research)
- **Comunidade Python Científica**: NumPy, SciPy, scikit-learn, Biopython

## 📞 Suporte

- 📧 **Email**: support@ftmap-enhanced.org
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/ftmap-enhanced/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/ftmap-enhanced/issues)
- 📚 **Wiki**: [GitHub Wiki](https://github.com/your-repo/ftmap-enhanced/wiki)

---

<div align="center">

**🎯 FTMap Enhanced v2.0**  
*Sistema Modular de Análise de Druggability*

[![GitHub stars](https://img.shields.io/github/stars/your-repo/ftmap-enhanced.svg?style=social&label=Star)](https://github.com/your-repo/ftmap-enhanced)
[![GitHub forks](https://img.shields.io/github/forks/your-repo/ftmap-enhanced.svg?style=social&label=Fork)](https://github.com/your-repo/ftmap-enhanced/fork)

</div>
