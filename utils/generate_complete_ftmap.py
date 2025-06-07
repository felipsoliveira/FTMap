#!/usr/bin/env python3
"""
Script para gerar arquivo PDB completo FTMap:
Proteína inteira + Clusters de fragmentos identificados
"""

import os
import sys
import glob
from collections import defaultdict
import numpy as np

def extract_poses_from_pdbqt(pdbqt_file):
    """Extrai todas as poses de um arquivo PDBQT"""
    poses = []
    current_pose = []
    energy = None
    
    with open(pdbqt_file, 'r') as f:
        for line in f:
            if line.startswith('MODEL'):
                current_pose = []
                energy = None
            elif line.startswith('REMARK VINA RESULT:'):
                # Extrai energia da linha REMARK
                parts = line.split()
                if len(parts) >= 4:
                    energy = float(parts[3])
            elif line.startswith('ATOM') or line.startswith('HETATM'):
                current_pose.append(line.strip())
            elif line.startswith('ENDMDL'):
                if current_pose and energy is not None:
                    poses.append({
                        'energy': energy,
                        'atoms': current_pose
                    })
                current_pose = []
    
    return sorted(poses, key=lambda x: x['energy'])

def calculate_pose_center(atoms):
    """Calcula centro geométrico de uma pose"""
    coords = []
    for atom_line in atoms:
        x = float(atom_line[30:38])
        y = float(atom_line[38:46]) 
        z = float(atom_line[46:54])
        coords.append([x, y, z])
    
    if coords:
        return np.mean(coords, axis=0)
    return None

def cluster_poses_by_distance(poses, distance_threshold=4.0):
    """Clustering simples por distância entre centros"""
    if not poses:
        return []
    
    clusters = []
    used_poses = set()
    
    for i, pose in enumerate(poses):
        if i in used_poses:
            continue
            
        center_i = calculate_pose_center(pose['atoms'])
        if center_i is None:
            continue
            
        cluster = [pose]
        used_poses.add(i)
        
        # Encontra poses próximas
        for j, other_pose in enumerate(poses):
            if j <= i or j in used_poses:
                continue
                
            center_j = calculate_pose_center(other_pose['atoms'])
            if center_j is None:
                continue
                
            distance = np.linalg.norm(center_i - center_j)
            if distance <= distance_threshold:
                cluster.append(other_pose)
                used_poses.add(j)
        
        clusters.append({
            'poses': cluster,
            'center': center_i,
            'best_energy': min(p['energy'] for p in cluster),
            'size': len(cluster)
        })
    
    return sorted(clusters, key=lambda x: x['best_energy'])

def generate_complete_ftmap_pdb():
    """Gera arquivo PDB completo com proteína + clusters"""
    
    # Diretórios
    base_dir = "/home/murilo/girias/ftmapcaseiro"
    results_dir = os.path.join(base_dir, "results")
    protein_file = os.path.join(base_dir, "protein_raw.pdb")
    
    if not os.path.exists(protein_file):
        print(f"❌ Arquivo de proteína não encontrado: {protein_file}")
        return
    
    print("🧬 Gerando FTMap completo: Proteína + Clusters")
    print("="*60)
    
    # Encontra arquivos PDBQT improved
    pdbqt_files = glob.glob(os.path.join(results_dir, "*_improved.pdbqt"))
    if not pdbqt_files:
        print("⚠️  Nenhum arquivo *_improved.pdbqt encontrado!")
        pdbqt_files = glob.glob(os.path.join(results_dir, "poses_probe_*.pdbqt"))
    
    print(f"📂 Encontrados {len(pdbqt_files)} arquivos de poses")
    
    # Processa cada fragmento
    all_clusters = []
    fragment_data = {}
    
    for pdbqt_file in pdbqt_files:
        filename = os.path.basename(pdbqt_file)
        if 'probe_' in filename:
            probe_name = filename.split('probe_')[1].split('_')[0].replace('.pdbqt', '')
        else:
            probe_name = filename.replace('.pdbqt', '')
        
        print(f"🔍 Processando {probe_name}...")
        
        poses = extract_poses_from_pdbqt(pdbqt_file)
        if not poses:
            print(f"  ⚠️  Nenhuma pose encontrada em {filename}")
            continue
        
        print(f"  📊 {len(poses)} poses encontradas")
        
        # Clustering
        clusters = cluster_poses_by_distance(poses[:50])  # Top 50 poses
        
        print(f"  🎯 {len(clusters)} clusters identificados")
        
        # Guarda os melhores clusters (top 6, como no FTMap original)
        top_clusters = clusters[:6]
        
        for i, cluster in enumerate(top_clusters):
            cluster_id = len(all_clusters)
            all_clusters.append({
                'id': cluster_id,
                'probe': probe_name,
                'cluster_rank': i,
                'center': cluster['center'],
                'energy': cluster['best_energy'],
                'size': cluster['size'],
                'best_pose': cluster['poses'][0]  # Melhor pose do cluster
            })
        
        fragment_data[probe_name] = {
            'total_poses': len(poses),
            'clusters': len(clusters),
            'best_energy': poses[0]['energy']
        }
    
    print(f"\n🎯 Total de clusters: {len(all_clusters)}")
    
    # Identifica hotspots de consenso
    consensus_sites = find_consensus_sites(all_clusters)
    
    print(f"🔥 Hotspots de consenso encontrados: {len(consensus_sites)}")
    
    # Gera arquivo PDB completo
    output_file = os.path.join(results_dir, "ftmap_complete_system.pdb")
    
    with open(output_file, 'w') as out:
        # Header
        out.write("REMARK FTMap Complete System - Protein + Fragment Clusters\n")
        out.write("REMARK Generated by FTMap Caseiro System\n")
        out.write("REMARK \n")
        out.write(f"REMARK Total fragments processed: {len(fragment_data)}\n")
        out.write(f"REMARK Total clusters identified: {len(all_clusters)}\n")
        out.write(f"REMARK Consensus sites found: {len(consensus_sites)}\n")
        out.write("REMARK \n")
        
        # Informações dos fragmentos
        out.write("REMARK Fragment Summary:\n")
        for probe, data in fragment_data.items():
            out.write(f"REMARK   {probe}: {data['total_poses']} poses, {data['clusters']} clusters, best: {data['best_energy']:.1f} kcal/mol\n")
        out.write("REMARK \n")
        
        # Hotspots de consenso
        if consensus_sites:
            out.write("REMARK Consensus Hotspots (ranked by size):\n")
            for i, site in enumerate(consensus_sites):
                fragments = [c['probe'] for c in site['clusters']]
                out.write(f"REMARK   Hotspot {i+1}: {len(site['clusters'])} fragments ({', '.join(fragments)})\n")
            out.write("REMARK \n")
        
        # Inclui proteína completa
        out.write("REMARK ===== PROTEIN STRUCTURE =====\n")
        with open(protein_file, 'r') as protein:
            for line in protein:
                if not line.startswith('HEADER') and not line.startswith('TITLE') and not line.startswith('COMPND'):
                    out.write(line)
        
        # Adiciona clusters de fragmentos
        out.write("REMARK ===== FRAGMENT CLUSTERS =====\n")
        
        atom_counter = 10000  # Começar numeração depois da proteína
        
        for cluster in all_clusters:
            probe = cluster['probe']
            energy = cluster['energy']
            size = cluster['size']
            
            out.write(f"REMARK Cluster {cluster['id']}: {probe} (Energy: {energy:.1f} kcal/mol, Size: {size})\n")
            
            # Atoms do melhor pose do cluster
            best_pose = cluster['best_pose']
            for atom_line in best_pose['atoms']:
                # Atualiza numeração dos átomos
                new_line = f"HETATM{atom_counter:5d}" + atom_line[11:]
                out.write(new_line + "\n")
                atom_counter += 1
            
            out.write("TER\n")
        
        out.write("END\n")
    
    print(f"\n✅ Arquivo completo gerado: {output_file}")
    print(f"📊 Tamanho: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # Gera relatório detalhado
    generate_analysis_report(fragment_data, all_clusters, consensus_sites, output_file.replace('.pdb', '_report.txt'))
    
    return output_file

def find_consensus_sites(clusters, distance_threshold=6.0):
    """Identifica sítios de consenso onde múltiplos fragmentos se ligam"""
    
    if len(clusters) < 2:
        return []
    
    consensus_sites = []
    used_clusters = set()
    
    for i, cluster_i in enumerate(clusters):
        if i in used_clusters:
            continue
        
        center_i = cluster_i['center']
        site_clusters = [cluster_i]
        used_clusters.add(i)
        
        # Procura clusters próximos de outros fragmentos
        for j, cluster_j in enumerate(clusters):
            if j <= i or j in used_clusters:
                continue
            
            # Só agrupa fragmentos diferentes
            if cluster_i['probe'] == cluster_j['probe']:
                continue
            
            center_j = cluster_j['center']
            distance = np.linalg.norm(center_i - center_j)
            
            if distance <= distance_threshold:
                site_clusters.append(cluster_j)
                used_clusters.add(j)
        
        # Só considera sítios com múltiplos fragmentos
        if len(site_clusters) >= 2:
            # Calcula centro médio do sítio
            centers = [c['center'] for c in site_clusters]
            avg_center = np.mean(centers, axis=0)
            
            consensus_sites.append({
                'clusters': site_clusters,
                'center': avg_center,
                'size': len(site_clusters),
                'avg_energy': np.mean([c['energy'] for c in site_clusters]),
                'fragments': list(set(c['probe'] for c in site_clusters))
            })
    
    # Ordena por tamanho (mais fragmentos = melhor hotspot)
    return sorted(consensus_sites, key=lambda x: x['size'], reverse=True)

def generate_analysis_report(fragment_data, clusters, consensus_sites, report_file):
    """Gera relatório detalhado da análise"""
    
    with open(report_file, 'w') as f:
        f.write("FTMAP COMPLETE SYSTEM - ANALYSIS REPORT\n")
        f.write("="*60 + "\n\n")
        
        # Resumo geral
        f.write("GENERAL SUMMARY\n")
        f.write("-"*20 + "\n")
        f.write(f"Fragments processed: {len(fragment_data)}\n")
        f.write(f"Total clusters: {len(clusters)}\n")
        f.write(f"Consensus sites: {len(consensus_sites)}\n\n")
        
        # Análise por fragmento
        f.write("FRAGMENT ANALYSIS\n")
        f.write("-"*20 + "\n")
        for probe, data in sorted(fragment_data.items()):
            f.write(f"{probe:15s}: {data['total_poses']:3d} poses, {data['clusters']:2d} clusters, ")
            f.write(f"best energy: {data['best_energy']:6.1f} kcal/mol\n")
        f.write("\n")
        
        # Clusters detalhados
        f.write("CLUSTER DETAILS\n")
        f.write("-"*20 + "\n")
        for cluster in clusters:
            f.write(f"Cluster {cluster['id']:2d}: {cluster['probe']:12s} ")
            f.write(f"Energy: {cluster['energy']:6.1f} kcal/mol, Size: {cluster['size']:2d}\n")
            f.write(f"           Center: ({cluster['center'][0]:7.2f}, {cluster['center'][1]:7.2f}, {cluster['center'][2]:7.2f})\n")
        f.write("\n")
        
        # Hotspots de consenso
        if consensus_sites:
            f.write("CONSENSUS HOTSPOTS\n")
            f.write("-"*20 + "\n")
            for i, site in enumerate(consensus_sites):
                f.write(f"Hotspot {i+1}: {site['size']} fragments\n")
                f.write(f"  Fragments: {', '.join(site['fragments'])}\n")
                f.write(f"  Average energy: {site['avg_energy']:.1f} kcal/mol\n")
                f.write(f"  Center: ({site['center'][0]:7.2f}, {site['center'][1]:7.2f}, {site['center'][2]:7.2f})\n")
                f.write("  Clusters:\n")
                for cluster in site['clusters']:
                    f.write(f"    - {cluster['probe']} (E: {cluster['energy']:.1f} kcal/mol)\n")
                f.write("\n")
        
        # Métricas de qualidade
        f.write("QUALITY METRICS\n")
        f.write("-"*20 + "\n")
        
        total_poses = sum(data['total_poses'] for data in fragment_data.values())
        f.write(f"Total poses analyzed: {total_poses}\n")
        
        if consensus_sites:
            primary_hotspot = consensus_sites[0]
            f.write(f"Primary hotspot size: {primary_hotspot['size']} fragments\n")
            f.write(f"Primary hotspot consensus: {primary_hotspot['size']/len(fragment_data)*100:.1f}%\n")
        
        energy_range = [cluster['energy'] for cluster in clusters]
        if energy_range:
            f.write(f"Energy range: {min(energy_range):.1f} to {max(energy_range):.1f} kcal/mol\n")
        
        f.write(f"\nConsensus sites in ideal range (10-20): {'✅ YES' if 10 <= len(consensus_sites) <= 20 else '❌ NO'}\n")

if __name__ == "__main__":
    try:
        output_file = generate_complete_ftmap_pdb()
        if output_file:
            print(f"\n🎉 Sistema FTMap completo gerado com sucesso!")
            print(f"📁 Arquivo: {output_file}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
