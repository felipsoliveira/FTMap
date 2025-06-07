# PyMOL Script para Visualização do Resultado Final FTMap Enhanced
# Carrega a proteína com os sites de ligação ranqueados

# Carregar estrutura final
load enhanced_outputs/ranked_results/ftmap_protein_with_ranked_sites.pdb, protein_with_sites

# Configurações básicas
bg_color white
set cartoon_transparency, 0.3
set sphere_scale, 0.8

# Mostrar proteína como cartoon
select protein, chain A
show cartoon, protein
color gray80, protein

# Colorir os sites de ligação por ranking
# Top 5 sites (vermelho - melhor)
select top_5, chain B+C+D+E+F
color red, top_5
show spheres, top_5

# Sites 6-10 (laranja - muito bom)
select top_10, chain G+H+I+J+K  
color orange, top_10
show spheres, top_10

# Sites 11-15 (amarelo - bom)
select top_15, chain L+M+N+O+P
color yellow, top_15
show spheres, top_15

# Sites 16-20 (verde - moderado)
select top_20, chain Q+R+S+T
color green, top_20
show spheres, top_20

# Labels para os top 5 sites
label chain B and name C, "Rank 1"
label chain C and name C, "Rank 2"
label chain D and name C, "Rank 3"
label chain E and name C, "Rank 4"
label chain F and name C, "Rank 5"

# Zoom para visualização completa
zoom
center protein

# Criar diferentes visualizações
scene 001, store, "Visão Geral"

# Foco no melhor site
zoom chain B
scene 002, store, "Melhor Site (Rank 1)"

# Foco nos top 5
zoom top_5
scene 003, store, "Top 5 Sites"

# Voltar à visão geral
scene 001, recall

print "=== FTMAP ENHANCED RESULTS ==="
print "Arquivo carregado: protein_with_sites"
print "Top 20 sites de ligação identificados"
print ""
print "CORES:"
print "  Vermelho = Top 5 (Ranks 1-5)"
print "  Laranja  = Top 10 (Ranks 6-10)"
print "  Amarelo  = Top 15 (Ranks 11-15)"
print "  Verde    = Top 20 (Ranks 16-20)"
print ""
print "CENAS:"
print "  001 = Visão Geral"
print "  002 = Melhor Site"
print "  003 = Top 5 Sites"
print ""
print "Comando: scene 001/002/003, recall"
