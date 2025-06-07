# Etapa 5: Scoring de Druggabilidade

## O que acontece nesta etapa:

1. **Cálculo do score de energia (25%)**
   - Avaliação da energia média de ligação do cluster
   - Priorização da faixa ideal de energia (-3 a -5 kcal/mol)
   - Penalização para energias muito fortes (artificial)
   - Normalização em escala 0-1

2. **Cálculo do score de diversidade (35%)**
   - Análise da diversidade química dos fragmentos
   - Contagem de grupos químicos distintos por cluster
   - Valorização de sítios que ligam diversos fragmentos
   - Normalização por diversidade máxima possível

3. **Cálculo do score de população (20%)**
   - Contagem do número de fragmentos por cluster
   - Valorização de sítios com maior número de fragmentos
   - Normalização logarítmica para evitar viés
   - Balanceamento com outros fatores

4. **Cálculo do score de compactação (20%)**
   - Medição da dispersão espacial dentro do cluster
   - Valorização de sítios compactos e bem definidos
   - Cálculo do raio de giro normalizado
   - Priorização de hotspots precisos

5. **Combinação dos scores**
   - Ponderação dos quatro componentes
   - Cálculo do score final de druggabilidade
   - Ranqueamento dos clusters
   - Identificação dos hotspots mais promissores

## Fórmula de scoring:
```
druggability_score = (0.25 * energy_score) + 
                    (0.35 * diversity_score) + 
                    (0.20 * population_score) + 
                    (0.20 * compactness_score)
```

## Entrada:
- Lista de clusters com suas propriedades
- Dados de energia, diversidade, população e compactação

## Saída:
- Scores de druggabilidade para cada cluster
- Ranking completo dos hotspots
- Relatório detalhado de scoring
- Arquivo PDB com os hotspots identificados

## Próximo passo:
→ Etapa 6: Visualização dos resultados
