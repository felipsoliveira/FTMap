# PyMOL Visualization Script for FTMap Enhanced Ranked Results
# Load the final PDB with protein + ranked binding sites

# Clear previous session
delete all
bg_color white

# Load the final PDB file with protein and ranked clusters
load enhanced_outputs/ranked_results/ftmap_protein_with_ranked_sites.pdb

# Set protein representation
select protein, chain A and not resn LIG
show cartoon, protein
color gray70, protein
set cartoon_transparency, 0.3

# Color top 10 binding sites with energy-based color scheme
select rank1, chain A and resn LIG and resi 1000
select rank2, chain B and resn LIG and resi 1001  
select rank3, chain C and resn LIG and resi 1002
select rank4, chain D and resn LIG and resi 1003
select rank5, chain E and resn LIG and resi 1004
select rank6, chain F and resn LIG and resi 1005
select rank7, chain G and resn LIG and resi 1006
select rank8, chain H and resn LIG and resi 1007
select rank9, chain I and resn LIG and resi 1008
select rank10, chain J and resn LIG and resi 1009

# Show binding sites as spheres with gradient colors
show spheres, resn LIG
set sphere_scale, 2.0

# Color scheme: Red (best) to Yellow (good) 
color red, rank1      # Best site (-5.18 kcal/mol)
color tv_red, rank2   # -6.53 kcal/mol
color orange, rank3   # -5.40 kcal/mol
color tv_orange, rank4  # -5.02 kcal/mol
color yellow, rank5   # -5.46 kcal/mol
color tv_yellow, rank6  # -6.34 kcal/mol
color paleyellow, rank7 # -7.26 kcal/mol (BEST ENERGY!)
color lightblue, rank8  # -5.11 kcal/mol
color blue, rank9     # -5.57 kcal/mol
color purple, rank10  # -5.61 kcal/mol

# Add labels for top 5 sites
label rank1 and name C and alt "", "RANK 1\n-5.18 kcal/mol"
label rank2 and name C and alt "", "RANK 2\n-6.53 kcal/mol"
label rank3 and name C and alt "", "RANK 3\n-5.40 kcal/mol"
label rank7 and name C and alt "", "RANK 7 (BEST ENERGY)\n-7.26 kcal/mol"
label rank10 and name C and alt "", "RANK 10\n-5.61 kcal/mol"

# Set view and zoom
zoom all
center protein

# Create surface representation for binding pockets
select surface_residues, protein within 5 of resn LIG
show surface, surface_residues
set surface_transparency, 0.7
color lightgray, surface_residues

# Final view settings
set ray_shadows, 0
set antialias, 2
set line_smooth, 1
set depth_cue, 1

print "="*60
print "FTMAP ENHANCED - RANKED BINDING SITES LOADED"
print "="*60
print "✅ Protein structure: Gray cartoon"
print "✅ Top 20 binding sites: Colored spheres"
print "✅ Binding pockets: Light gray surface"
print ""
print "🏆 TOP RANKED SITES:"
print "   RANK 1 (RED): -5.18 kcal/mol"
print "   RANK 2 (TV_RED): -6.53 kcal/mol" 
print "   RANK 7 (PALE_YELLOW): -7.26 kcal/mol (BEST ENERGY!)"
print ""
print "💡 Use 'zoom rank1' to focus on top site"
print "💡 Use 'orient' to reset view"
print "="*60
