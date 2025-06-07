# PyMOL Visualization Script for FTMap Enhanced Results
# pfpkii.pdb (Pyruvate Kinase 2) + FTMap Enhanced Clusters

# Clear and load structure
delete all
bg_color white
load pfpkii_with_ftmap_clusters.pdb

# Protein representation
select protein, chain A
show cartoon, protein
color gray70, protein
set cartoon_transparency, 0.3

# Enhanced FTMap clusters visualization
select cluster1, chain B
show spheres, cluster1
color red, cluster1
select cluster2, chain C
show spheres, cluster2
color orange, cluster2
select cluster3, chain D
show spheres, cluster3
color yellow, cluster3
select cluster4, chain E
show spheres, cluster4
color green, cluster4
select cluster5, chain F
show spheres, cluster5
color blue, cluster5

set sphere_scale, 2.0
zoom all
