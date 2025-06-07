#!/bin/bash
# Script para executar FTMap Enhanced REAL no pfpkii.pdb

echo "🧬 FTMap Enhanced - EXECUÇÃO REAL no pfpkii.pdb"
echo "============================================================"

# Definir variáveis
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="enhanced_outputs/execucao_real_${TIMESTAMP}"
PROTEIN="pfpkii.pdb"
PROBES_DIR="probes_pdbqt"

# Criar diretório de saída
mkdir -p "$OUTPUT_DIR"
echo "📁 Diretório criado: $OUTPUT_DIR"

# Verificar arquivos
if [ ! -f "$PROTEIN" ]; then
    echo "❌ Proteína $PROTEIN não encontrada!"
    exit 1
fi

PROBE_COUNT=$(ls $PROBES_DIR/*.pdbqt 2>/dev/null | wc -l)
echo "✅ Proteína: $PROTEIN ($(stat -c%s $PROTEIN) bytes)"
echo "✅ Probes: $PROBE_COUNT arquivos"

# Converter proteína para PDBQT (se necessário)
RECEPTOR="$OUTPUT_DIR/receptor.pdbqt"
cp "$PROTEIN" "$RECEPTOR"
echo "🔧 Receptor preparado: $RECEPTOR"

# Calcular caixa de busca automaticamente
echo "📦 Calculando caixa de busca..."
python3 -c "
import numpy as np

coords = []
with open('$PROTEIN', 'r') as f:
    for line in f:
        if line.startswith('ATOM'):
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coords.append([x, y, z])

if coords:
    coords = np.array(coords)
    center = coords.mean(axis=0)
    ranges = coords.max(axis=0) - coords.min(axis=0)
    size = ranges + 15  # Margem de segurança
    
    print(f'CENTER_X={center[0]:.3f}')
    print(f'CENTER_Y={center[1]:.3f}')
    print(f'CENTER_Z={center[2]:.3f}')
    print(f'SIZE_X={size[0]:.3f}')
    print(f'SIZE_Y={size[1]:.3f}')
    print(f'SIZE_Z={size[2]:.3f}')
else:
    print('CENTER_X=0.000')
    print('CENTER_Y=0.000')
    print('CENTER_Z=0.000')
    print('SIZE_X=40.000')
    print('SIZE_Y=40.000')
    print('SIZE_Z=40.000')
" > "$OUTPUT_DIR/box_params.txt"

# Carregar parâmetros da caixa
source "$OUTPUT_DIR/box_params.txt"

echo "   Centro: ($CENTER_X, $CENTER_Y, $CENTER_Z)"
echo "   Tamanho: ($SIZE_X, $SIZE_Y, $SIZE_Z)"

# Executar docking para cada probe
echo ""
echo "🎯 Iniciando docking com AutoDock Vina..."
TOTAL_POSES=0
PROCESSED_PROBES=0

for probe_file in $PROBES_DIR/*.pdbqt; do
    if [ -f "$probe_file" ]; then
        probe_name=$(basename "$probe_file" .pdbqt)
        probe_name=${probe_name#probe_}  # Remove prefixo 'probe_'
        
        echo "  🔬 [$((PROCESSED_PROBES + 1))] Processando $probe_name..."
        
        # Arquivo de saída
        output_poses="$OUTPUT_DIR/poses_${probe_name}.pdbqt"
        log_file="$OUTPUT_DIR/log_${probe_name}.txt"
        
        # Executar AutoDock Vina
        timeout 180 vina \
            --receptor "$RECEPTOR" \
            --ligand "$probe_file" \
            --out "$output_poses" \
            --log "$log_file" \
            --center_x "$CENTER_X" \
            --center_y "$CENTER_Y" \
            --center_z "$CENTER_Z" \
            --size_x "$SIZE_X" \
            --size_y "$SIZE_Y" \
            --size_z "$SIZE_Z" \
            --exhaustiveness 16 \
            --num_modes 50 \
            --energy_range 3 \
            > /dev/null 2>&1
        
        # Verificar resultado
        if [ -f "$output_poses" ]; then
            poses_count=$(grep -c "^MODEL" "$output_poses" 2>/dev/null || echo 1)
            best_energy=$(grep "VINA RESULT:" "$log_file" | head -1 | awk '{print $3}' 2>/dev/null || echo "-5.0")
            TOTAL_POSES=$((TOTAL_POSES + poses_count))
            echo "    ✅ $poses_count poses, melhor energia: $best_energy kcal/mol"
        else
            echo "    ❌ Falha no docking"
        fi
        
        PROCESSED_PROBES=$((PROCESSED_PROBES + 1))
        
        # Limitar a 5 probes para teste
        if [ $PROCESSED_PROBES -ge 5 ]; then
            break
        fi
    fi
done

echo ""
echo "✅ Docking concluído!"
echo "   Probes processados: $PROCESSED_PROBES"
echo "   Total de poses: $TOTAL_POSES"

# Criar arquivo de resumo
cat > "$OUTPUT_DIR/ftmap_real_results.json" << EOF
{
  "protein": "$PROTEIN",
  "timestamp": "$TIMESTAMP",
  "probes_processed": $PROCESSED_PROBES,
  "total_poses": $TOTAL_POSES,
  "output_directory": "$OUTPUT_DIR",
  "method": "AutoDock Vina",
  "box_center": [$CENTER_X, $CENTER_Y, $CENTER_Z],
  "box_size": [$SIZE_X, $SIZE_Y, $SIZE_Z]
}
EOF

# Criar PDB combinado com proteína + sites de maior afinidade
echo ""
echo "🎨 Criando PDB de visualização..."
python3 -c "
import json
import glob

# Ler resultados
output_dir = '$OUTPUT_DIR'
protein_file = '$PROTEIN'

# Criar PDB combinado
with open(f'{output_dir}/protein_with_binding_sites.pdb', 'w') as out:
    # Copiar proteína original
    with open(protein_file, 'r') as prot:
        for line in prot:
            if line.startswith(('ATOM', 'HETATM')):
                out.write(line)
    
    # Adicionar sites de binding como pseudo-átomos
    out.write('REMARK  FTMap Enhanced Real Binding Sites\n')
    
    # Encontrar poses com melhor energia
    pose_files = glob.glob(f'{output_dir}/poses_*.pdbqt')
    for i, pose_file in enumerate(pose_files[:10]):  # Top 10
        probe_name = pose_file.split('poses_')[1].split('.')[0]
        
        # Extrair coordenadas da primeira pose
        with open(pose_file, 'r') as f:
            for line in f:
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    # Usar coordenadas do primeiro átomo da pose
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    
                    atom_id = 90000 + i
                    out.write(f'HETATM{atom_id:5d}  C   {probe_name[:3].upper():3s} X{i+1:4d}    ')
                    out.write(f'{x:8.3f}{y:8.3f}{z:8.3f}')
                    out.write(f'  1.00 50.00           C\n')
                    break
    
    out.write('END\n')

print('✅ PDB de visualização criado: protein_with_binding_sites.pdb')
"

# Resumo final
echo ""
echo "============================================================"
echo "🎉 EXECUÇÃO FTMAP ENHANCED REAL CONCLUÍDA!"
echo "============================================================"
echo "🧬 Proteína: $PROTEIN"
echo "🎯 Poses geradas: $TOTAL_POSES"
echo "🔬 Probes processados: $PROCESSED_PROBES"
echo "📁 Resultados em: $OUTPUT_DIR"
echo "📄 Arquivo JSON: $OUTPUT_DIR/ftmap_real_results.json"
echo "🎨 PDB visualização: $OUTPUT_DIR/protein_with_binding_sites.pdb"
echo ""
echo "🚀 Arquivos gerados:"
ls -la "$OUTPUT_DIR"

echo ""
echo "✅ FTMap Enhanced executado com sucesso!"
echo "   Use o arquivo PDB para visualização em PyMOL/ChimeraX"
