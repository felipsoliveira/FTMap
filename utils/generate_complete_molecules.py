#!/usr/bin/env python3
"""
Generate Complete Molecule PDB with all fragments
Creates a complete PDB file with all processed fragments
"""

import os
import glob
import re
import sys

def parse_pdbqt_energy(pdbqt_file):
    """Extract best energy from PDBQT file"""
    try:
        with open(pdbqt_file, 'r') as f:
            for line in f:
                if "REMARK VINA RESULT" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        return float(parts[3])
        return 0.0
    except:
        return 0.0

def get_fragment_name(filename):
    """Extract fragment name from filename"""
    base = os.path.basename(filename)
    match = re.search(r'poses_probe_(.+?)_improved\.pdbqt', base)
    if match:
        return match.group(1)
    return "Unknown"

def convert_pdbqt_to_pdb_section(pdbqt_file, fragment_name, chain_id, model_num):
    """Convert first model of PDBQT to PDB section"""
    pdb_lines = []
    atom_count = 0
    current_model = 0
    reading_model = False
    
    # Get energy
    energy = parse_pdbqt_energy(pdbqt_file)
    
    try:
        with open(pdbqt_file, 'r') as f:
            pdb_lines.append(f"REMARK Chain {chain_id}: {fragment_name} (Energy: {energy:.1f} kcal/mol)")
            
            for line in f:
                if line.startswith("MODEL"):
                    current_model = int(line.strip().split()[1])
                    reading_model = (current_model == 1)  # Only read model 1
                    continue
                    
                if line.startswith("ENDMDL"):
                    reading_model = False
                    continue
                    
                if not reading_model:
                    continue
                    
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    atom_count += 1
                    # Format: HETATM atom_num atom_name res_name chain res_num x y z occupancy temp_factor element
                    # Example: HETATM    1  C   BEN B   2      -6.375   1.013   7.648  1.00  0.00           C
                    
                    # Extract coordinates and atom info
                    atom_name = line[12:16].strip()
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip())
                    z = float(line[46:54].strip())
                    
                    # Create abbreviation (first 3 letters)
                    abbrev = fragment_name[:3].upper()
                    
                    # Format as PDB HETATM line
                    pdb_line = f"HETATM{atom_count:5d}  {atom_name:<3} {abbrev} {chain_id} {model_num:3d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           {atom_name[0]}"
                    pdb_lines.append(pdb_line)
            
            pdb_lines.append("TER")
    except Exception as e:
        print(f"Error processing {pdbqt_file}: {str(e)}")
    
    return pdb_lines

def generate_complete_pdb(results_dir, output_file):
    """Generate complete PDB with all fragments"""
    pose_files = glob.glob(os.path.join(results_dir, "poses_probe_*_improved.pdbqt"))
    pose_files.sort()  # Ensure consistent order
    
    if not pose_files:
        print("No pose files found!")
        return False
    
    print(f"Found {len(pose_files)} fragment files")
    
    pdb_lines = [
        "REMARK FTMap Complete Molecules - Best Poses",
        "REMARK Generated from AutoDock Vina docking results",
        "REMARK Each chain represents a different probe molecule",
        "REMARK Coordinates show the best binding pose for each probe",
        "REMARK"
    ]
    
    chain_ids = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for i, pose_file in enumerate(pose_files):
        fragment_name = get_fragment_name(pose_file)
        chain_id = chain_ids[i % len(chain_ids)]
        model_num = i + 1
        
        print(f"Processing {fragment_name} (Chain {chain_id})")
        section = convert_pdbqt_to_pdb_section(pose_file, fragment_name, chain_id, model_num)
        pdb_lines.extend(section)
    
    pdb_lines.append("END")
    
    # Write output file
    with open(output_file, 'w') as f:
        for line in pdb_lines:
            f.write(line + "\n")
    
    print(f"Generated PDB with {len(pose_files)} fragments: {output_file}")
    return True

if __name__ == "__main__":
    results_dir = "results"
    output_file = os.path.join(results_dir, "ftmap_complete_molecules.pdb")
    
    print("Generating Complete Molecules PDB")
    print("=================================")
    
    success = generate_complete_pdb(results_dir, output_file)
    
    if success:
        print("✅ Complete PDB file generated successfully!")
    else:
        print("❌ Failed to generate complete PDB file!")
