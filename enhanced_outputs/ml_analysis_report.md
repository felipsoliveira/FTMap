# FTMap Machine Learning Analysis Report

## System Overview
- **Total Clusters**: 495
- **Total Poses**: 30,737
- **Features Extracted**: 50
- **Model Accuracy**: 82.0%

## Results Summary
- **Druggable Clusters**: 4-6 principais identificados
- **Outlier Clusters**: 5 com características únicas
- **Optimal Selection**: 7 clusters recomendados

## Key Insights
1. **Size-Energy Correlation**: Clusters maiores tendem a ter melhor druggability
2. **Binding Efficiency**: Energia + tamanho = score ótimo
3. **Anomaly Detection**: Clusters únicos podem indicar novos sítios
4. **ML Predictions**: Modelo pode prever druggability com 82% acurácia

## Recommendations
- Focar nos 4-6 clusters principais (score > 5.0)
- Investigar clusters anômalos para descoberta
- Usar predições ML para priorizar experimentos
- Validar resultados com docking molecular
