#!/bin/bash
# 🔥 ULTRA RÁPIDO - SÓ RODA A PORRA DO ALGORITMO! 

cd /home/murilo/girias/ftmapcaseiro

# Ativar ambiente se existir
[ -d enhanced_env ] && source enhanced_env/bin/activate

echo "🔥🔥🔥 RODANDO PFPKII.PDB NO FTMAP ENHANCED 🔥🔥🔥"

# Executar direto
python3 -c "
import sys
sys.path.append('ftmap_enhanced_final/src')

from ftmap_enhanced_algorithm import FTMapEnhancedAlgorithm
from pathlib import Path
from datetime import datetime

# Setup
protein_file = 'pfpkii.pdb'
probes_dir = 'probes_pdbqt'
output_dir = Path(f'enhanced_outputs/ultra_rapido_{datetime.now().strftime(\"%H%M%S\")}')
output_dir.mkdir(parents=True, exist_ok=True)

print(f'🎯 Proteína: {protein_file}')
print(f'🧪 Probes: {probes_dir}')
print(f'📊 Output: {output_dir}')
print()

# EXECUTAR!
try:
    algorithm = FTMapEnhancedAlgorithm(protein_file=protein_file)
    results = algorithm.run_enhanced_analysis(
        protein_file=protein_file,
        probes_dir=probes_dir,
        output_dir=str(output_dir)
    )
    print('🎉 SUCESSO TOTAL!')
    print(f'📁 Resultados em: {output_dir}')
except Exception as e:
    print(f'💥 ERRO: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🏆 EXECUÇÃO CONCLUÍDA!"
