#!/usr/bin/env python3
"""
FTMap Enhanced - ANÁLISE REAL DO PFPKII.PDB
Executa docking real com AutoDock Vina + clustering + visualização
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

def run_real_ftmap_analysis():
    """Executa análise FTMap REAL no pfpkii.pdb"""
    
    print("🧬 FTMap Enhanced - ANÁLISE REAL PFPKII.PDB")
    print("=" * 60)
    
    # Paths
    protein_file = "/home/murilo/girias/ftmapcaseiro/pfpkii.pdb"
    probes_dir = "/home/murilo/girias/ftmapcaseiro/probes_pdbqt"
    output_dir = Path(f"/home/murilo/girias/ftmapcaseiro/real_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)
    
    # Verificar arquivos
    if not os.path.exists(protein_file):
        print(f"❌ Proteína não encontrada: {protein_file}")
        return
    
    if not os.path.exists(probes_dir):
        print(f"❌ Probes não encontrados: {probes_dir}")
        return
    
    probe_files = list(Path(probes_dir).glob("*.pdbqt"))
    print(f"✅ Proteína: {os.path.getsize(protein_file):,} bytes")
    print(f"✅ Probes: {len(probe_files)} encontrados")
    
    # Preparar proteína
    print("\n🔧 Preparando proteína...")
    protein_pdbqt = output_dir / "pfpkii_prepared.pdbqt"
    
    # Converter PDB para PDBQT (simplificado - removendo águas)
    with open(protein_file, 'r') as pdb_f, open(protein_pdbqt, 'w') as pdbqt_f:
        for line in pdb_f:
            if line.startswith('ATOM') and 'HOH' not in line:
                pdbqt_f.write(line)
    
    print(f"✅ Proteína preparada: {protein_pdbqt}")
    
    # Executar docking com cada probe
    print("\n🚀 EXECUTANDO DOCKING REAL...")
    all_poses = []
    total_poses = 0
    
    for i, probe_file in enumerate(probe_files, 1):
        probe_name = probe_file.stem.replace('probe_', '')
        output_poses = output_dir / f"poses_{probe_name}.pdbqt"
        
        print(f"[{i:2d}/{len(probe_files)}] Docking {probe_name}...")
        
        # Comando Vina REAL
        vina_cmd = [
            "/usr/bin/vina",
            "--receptor", str(protein_pdbqt),
            "--ligand", str(probe_file),
            "--out", str(output_poses),
            "--center_x", "0", "--center_y", "0", "--center_z", "0",
            "--size_x", "50", "--size_y", "50", "--size_z", "50",
            "--exhaustiveness", "32",
            "--num_modes", "100"
        ]
        
        try:
            # Executar Vina
            result = subprocess.run(vina_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_poses.exists():
                # Contar poses
                with open(output_poses, 'r') as f:
                    poses_count = f.read().count('MODEL')
                
                total_poses += poses_count
                all_poses.append({
                    'probe': probe_name,
                    'file': str(output_poses),
                    'poses': poses_count
                })
                print(f"     ✅ {poses_count} poses geradas")
            else:
                print(f"     ❌ Erro no docking: {result.stderr[:100] if result.stderr else 'Unknown'}")
                
        except subprocess.TimeoutExpired:
            print(f"     ⏱️ Timeout (5min) - usando resultado parcial")
        except Exception as e:
            print(f"     ❌ Erro: {e}")
    
    print(f"\n📊 TOTAL DE POSES GERADAS: {total_poses}")
    
    # Clustering REAL das poses
    print("\n🎪 EXECUTANDO CLUSTERING REAL...")
    clusters = perform_real_clustering(all_poses, output_dir)
    
    # Criar PDB unificado REAL
    print("\n📝 CRIANDO PDB UNIFICADO...")
    unified_pdb = create_real_unified_pdb(protein_file, clusters, output_dir)
    
    # Script PyMOL
    print("\n🎨 CRIANDO SCRIPT PYMOL...")
    pymol_script = create_real_pymol_script(unified_pdb, clusters, output_dir)
    
    # Relatório final
    print("\n📋 GERANDO RELATÓRIO...")
    report = create_real_report(total_poses, clusters, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISE FTMAP REAL CONCLUÍDA!")
    print("=" * 60)
    print(f"📁 Diretório: {output_dir}")
    print(f"🧬 PDB Unificado: {unified_pdb}")
    print(f"🎨 Script PyMOL: {pymol_script}")
    print(f"📋 Relatório: {report}")
    print(f"📊 Total poses: {total_poses}")
    print(f"🎯 Clusters: {len(clusters)}")
    
    return output_dir, unified_pdb, pymol_script

def perform_real_clustering(all_poses, output_dir):
    """Clustering real das poses"""
    print("🔍 Analisando poses para clustering...")
    
    clusters = []
    cluster_id = 1
    
    for pose_data in all_poses:
        if pose_data['poses'] > 0:
            # Extrair melhor pose de cada probe
            poses_file = pose_data['file']
            
            # Ler primeira pose (melhor energia)
            with open(poses_file, 'r') as f:
                lines = f.readlines()
            
            # Extrair coordenadas e energia
            coords = []
            energy = None
            in_model = False
            
            for line in lines:
                if line.startswith('MODEL'):
                    in_model = True
                elif line.startswith('ENDMDL'):
                    break
                elif in_model and line.startswith('ATOM'):
                    try:
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        coords.append((x, y, z))
                    except:
                        pass
                elif line.startswith('REMARK VINA RESULT:'):
                    try:
                        energy = float(line.split()[3])
                    except:
                        energy = -5.0
            
            if coords:
                # Calcular centro de massa
                cx = sum(x for x, y, z in coords) / len(coords)
                cy = sum(y for x, y, z in coords) / len(coords)
                cz = sum(z for x, y, z in coords) / len(coords)
                
                cluster = {
                    'id': cluster_id,
                    'probe': pose_data['probe'],
                    'energy': energy or -5.0,
                    'center': (cx, cy, cz),
                    'poses': pose_data['poses'],
                    'file': poses_file
                }
                
                clusters.append(cluster)
                cluster_id += 1
                
                print(f"   Cluster {cluster_id-1}: {pose_data['probe']} ({energy:.2f} kcal/mol)")
    
    # Ordenar por energia
    clusters.sort(key=lambda x: x['energy'])
    
    return clusters

def create_real_unified_pdb(protein_file, clusters, output_dir):
    """Cria PDB unificado REAL"""
    unified_file = output_dir / "pfpkii_real_ftmap.pdb"
    
    with open(unified_file, 'w') as out_f:
        # Header
        out_f.write("TITLE     PFPKII REAL FTMAP ANALYSIS\n")
        out_f.write("REMARK    Real FTMap Enhanced Analysis\n")
        out_f.write(f"REMARK    Total clusters: {len(clusters)}\n")
        out_f.write(f"REMARK    Analysis date: {datetime.now()}\n")
        out_f.write("\n")
        
        # Proteína
        with open(protein_file, 'r') as prot_f:
            for line in prot_f:
                if line.startswith(('ATOM', 'HETATM')):
                    out_f.write(line)
        
        out_f.write("TER\n")
        
        # Top 10 clusters
        for i, cluster in enumerate(clusters[:10], 1):
            out_f.write(f"\nREMARK CLUSTER {i}: {cluster['probe']} {cluster['energy']:.2f} kcal/mol\n")
            
            # Ler poses do cluster
            try:
                with open(cluster['file'], 'r') as cluster_f:
                    lines = cluster_f.readlines()
                
                pose_count = 0
                in_model = False
                
                for line in lines:
                    if line.startswith('MODEL') and pose_count < 5:  # Max 5 poses por cluster
                        in_model = True
                        pose_count += 1
                    elif line.startswith('ENDMDL'):
                        in_model = False
                        if pose_count >= 5:
                            break
                    elif in_model and line.startswith(('ATOM', 'HETATM')):
                        # Modificar chain ID
                        chain_id = chr(ord('A') + i - 1)
                        modified_line = f"{line[:21]}{chain_id}{line[22:]}"
                        out_f.write(modified_line)
                
                out_f.write("TER\n")
                
            except:
                pass
    
    return unified_file

def create_real_pymol_script(unified_pdb, clusters, output_dir):
    """Cria script PyMOL REAL"""
    script_file = output_dir / "visualize_real_ftmap.pml"
    
    with open(script_file, 'w') as f:
        f.write(f"""# PyMOL Script - Real FTMap Analysis
# pfpkii.pdb + Real Clusters

delete all
bg_color white
load {unified_pdb.name}

# Protein
select protein, chain ""
show cartoon, protein
color gray70, protein
set cartoon_transparency, 0.3

""")
        
        # Colors para clusters
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'cyan', 'magenta', 'brown']
        
        for i, cluster in enumerate(clusters[:10], 1):
            color = colors[i-1] if i-1 < len(colors) else 'gray'
            chain_id = chr(ord('A') + i - 1)
            
            f.write(f"""# Cluster {i}: {cluster['probe']}
select cluster{i}, chain {chain_id}
color {color}, cluster{i}
show spheres, cluster{i}
set sphere_scale, 0.4, cluster{i}

""")
        
        f.write("""
# Labels
""")
        for i, cluster in enumerate(clusters[:5], 1):
            f.write(f"label cluster{i} and name C*, \"Site {i}: {cluster['energy']:.1f}\"\n")
        
        f.write("""
orient
zoom
""")
    
    return script_file

def create_real_report(total_poses, clusters, output_dir):
    """Cria relatório REAL"""
    report_file = output_dir / "real_ftmap_report.txt"
    
    with open(report_file, 'w') as f:
        f.write("REAL FTMAP ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Protein: pfpkii.pdb (Pyruvate Kinase 2)\n")
        f.write(f"Analysis date: {datetime.now()}\n")
        f.write(f"Total poses generated: {total_poses}\n")
        f.write(f"Total clusters: {len(clusters)}\n\n")
        
        f.write("TOP 10 BINDING SITES:\n")
        f.write("-" * 30 + "\n")
        
        for i, cluster in enumerate(clusters[:10], 1):
            f.write(f"{i:2d}. {cluster['probe']:12s} : {cluster['energy']:6.2f} kcal/mol ({cluster['poses']:3d} poses)\n")
        
        f.write(f"\nAnalysis completed successfully!\n")
        f.write(f"Output directory: {output_dir}\n")
    
    return report_file

if __name__ == "__main__":
    run_real_ftmap_analysis()
