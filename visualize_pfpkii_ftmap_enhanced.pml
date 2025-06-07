# PyMOL Script - FTMap Enhanced Results
# pfpkii.pdb + Top 10 Druggable Sites

# Load structure
delete all
bg_color white
load pfpkii_complete_ftmap_enhanced.pdb

# Protein representation
select protein, chain ""
show cartoon, protein
color gray70, protein
set cartoon_transparency, 0.3

# Top druggable sites (clusters)
select cluster1, chain A
color red, cluster1
show spheres, cluster1
set sphere_scale, 0.3, cluster1

select cluster2, chain B  
color orange, cluster2
show spheres, cluster2
set sphere_scale, 0.3, cluster2

select cluster3, chain C
color yellow, cluster3
show spheres, cluster3
set sphere_scale, 0.3, cluster3

select cluster4, chain D
color green, cluster4
show spheres, cluster4
set sphere_scale, 0.3, cluster4

select cluster5, chain E
color blue, cluster5
show spheres, cluster5
set sphere_scale, 0.3, cluster5

select cluster6, chain F
color purple, cluster6
show spheres, cluster6
set sphere_scale, 0.3, cluster6

select cluster7, chain G
color pink, cluster7
show spheres, cluster7
set sphere_scale, 0.3, cluster7

select cluster8, chain H
color cyan, cluster8
show spheres, cluster8
set sphere_scale, 0.3, cluster8

select cluster9, chain I
color magenta, cluster9
show spheres, cluster9
set sphere_scale, 0.3, cluster9

select cluster10, chain J
color brown, cluster10
show spheres, cluster10
set sphere_scale, 0.3, cluster10

# Labels
label cluster1 and name C1, "Site 1: -11.24"
label cluster2 and name C1, "Site 2: -11.15"
label cluster3 and name C1, "Site 3: -10.91"

# View
orient
zoom
