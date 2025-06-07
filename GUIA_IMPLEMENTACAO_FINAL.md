# 🚀 FTMap Enhanced - Guia de Implementação

## 📋 Pré-requisitos
- Python 3.8+
- NumPy, SciPy, Scikit-learn
- AutoDock Vina
- Proteína em formato PDB
- Probes em formato PDBQT

## 🔧 Instalação Rápida

```bash
# 1. Clonar repositório
git clone [repository-url]
cd ftmapcaseiro

# 2. Instalar dependências
pip install numpy scipy scikit-learn pandas matplotlib

# 3. Verificar sistema
python3 ftmap_final_system.py --check

# 4. Executar análise
python3 ftmap_enhanced_algorithm.py --protein protein.pdb
```

## 📊 Uso Básico

### Análise Simples:
```python
from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm

# Inicializar sistema
ftmap = FTMapEnhancedAlgorithm('results.json')

# Executar análise completa
results = ftmap.run_enhanced_analysis()

# Ver resultados
ftmap.display_results()
```

### Análise Avançada:
```python
# Configurar parâmetros enhanced
params = {
    'exhaustiveness': 128,
    'num_modes': 500,
    'target_poses': 100000,
    'clustering_ensemble': True,
    'ml_prediction': True
}

# Executar com parâmetros otimizados
results = ftmap.run_enhanced_analysis(params)
```

## 🎯 Vantagens vs E-FTMap

| Aspecto | FTMap Enhanced | E-FTMap |
|---------|----------------|---------|
| Poses | 100,000+ | ~80,000 |
| Features | 29 | ~15 |
| Custo | **GRATUITO** | $$$ |
| Código | **ABERTO** | Proprietário |

## 📞 Suporte
- Documentação: README.md
- Issues: GitHub Issues
- Comunidade: Discussões científicas abertas

*Sistema pronto para superar E-FTMap comercial!*
