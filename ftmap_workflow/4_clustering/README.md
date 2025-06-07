# Etapa 4: Clustering das Poses

## O que acontece nesta etapa:

1. **Preparação para clustering**
   - Carregamento dos dados de poses e energias
   - Cálculo de centros de massa para cada fragmento
   - Conversão para formato matricial otimizado
   - Normalização de coordenadas espaciais

2. **Aplicação do algoritmo DBSCAN**
   - Clustering baseado em densidade espacial
   - Parâmetros: eps=4.0Å, min_samples=2
   - Identificação de regiões de alta densidade de poses
   - Tratamento adequado de outliers

3. **Clustering com ponderação Boltzmann**
   - Cálculo dos pesos de Boltzmann para cada pose:
     ```
     weight = exp(-energy * beta)  # beta = 1/(kB*T)
     ```
   - Ponderação das posições com base nas energias
   - Identificação de clusters energeticamente favoráveis
   - Cálculo de centros ponderados por energia

4. **Análise de clusters**
   - Contagem de fragmentos por cluster
   - Cálculo de energia média por cluster
   - Determinação da diversidade química por cluster
   - Medição da compactação espacial dos clusters

## Algoritmos implementados:
- DBSCAN para clustering baseado em densidade
- Clustering hierárquico para análise complementar
- Ponderação Boltzmann para priorização energética
- Métricas de diversidade e compactação customizadas

## Entrada:
- Estruturas de dados com poses e energias
- Arquivo PDB compilado com todos os fragmentos

## Saída:
- Lista de clusters identificados
- Informações detalhadas de cada cluster
- Estatísticas de agrupamento
- Dados preparados para scoring

## Próximo passo:
→ Etapa 5: Scoring de druggabilidade
