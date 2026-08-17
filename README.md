# Análise de Dados de Voos com ênfase na Meteorologia Local

Este projeto realiza uma análise exploratória de dados (EDA) para responder a perguntas propostas sobre a relação entre condições meteorológicas e operações de voos em um único período sazonal. Utiliza Python com as bibliotecas Pandas, NumPy, Matplotlib e demais, para processar e analisar dados de voos (mês de julho, nos anos de 2023, 2024 e 2025) e dados meteorológicos correspondentes as mesmas datas. Todavia, importa dizer que estes dados são totalmente fictícios com propósito único de treinar o uso do Python em suas bibliotecas. 

---

## Organização dos Dados

O sistema espera **6 arquivos CSV**:

| Arquivo | Descrição | Colunas principais |
| :--- | :--- | :--- |
| `voos_2023.csv` | Voos realizados em julho/2023 | `id_voo`, `aeroporto_origem`, `aeroporto_destino`, `data`, `horario_previsto`, `status`, `atraso_minutos`, `cancelado`, `motivo_atraso` |
| `voos_2024.csv` | Voos realizados em julho/2024 | *(mesma estrutura)* |
| `voos_2025.csv` | Voos realizados em julho/2025 | *(mesma estrutura)* |
| `meteorologia_aeroportos_2023.csv` | Dados meteorológicos horários para julho/2023 | `id_registro_meteo`, `aeroporto`, `data_hora`, `temperatura_c`, `pressao_hpa`, `visibilidade_m`, `vento_kmh`, `rajada_kmh`, `precipitacao_mm`, `cobertura_nuvens_pct`, `condicao_meteorologica` |
| `meteorologia_aeroportos_2024.csv` | Dados meteorológicos para julho/2024 | *(mesma estrutura)* |
| `meteorologia_aeroportos_2025.csv` | Dados meteorológicos para julho/2025 | *(mesma estrutura)* |


---

## Principais Tecnologias Utilizadas

| Ferramenta | Para que serve neste projeto? (De forma simples) |
| :--- | :--- |
| **Python 3.12+** | O "cérebro" do projeto; a linguagem de programação usada para escrever todo o código. |
| **Pandas** | Organiza os dados em tabelas (como no Excel) para facilitar a limpeza e a união dos arquivos. |
| **NumPy** | Ajuda a fazer cálculos matemáticos rápidos e a criar dados de teste para simular o clima. |
| **Matplotlib** | Ferramenta básica para desenhar e salvar os gráficos no seu computador. |
| **Seaborn** | Deixa os gráficos do Matplotlib mais bonitos, coloridos e fáceis de entender. |
| **os** | Cria automaticamente a pasta `img/` no seu computador para guardar os gráficos gerados. |

# Explicação da Saída do Script

Abaixo está a interpretação detalhada de cada bloco de saída gerado pelo script `veranalise.py`. Essas informações ajudam a entender os resultados e a validade das conclusões.

## Mensagem Inicial

```text
Dados carregados:
  Voos: 3720 registros
  Meteorologia: 4650 registros

```

* **Voos**: 3.720 registros (3 anos × 31 dias × 40 voos/dia).
* **Meteorologia**: 4.650 registros (3 anos × 31 dias × 10 aeroportos × 5 horários).
* **Injeção de dados**: O script injetou 177 registros sintéticos (5% dos voos realizados) com visibilidade entre 500 e 4.500 m para permitir a análise da faixa "Muito baixa (<5000m)".

---

## Atraso Médio por Faixa de Visibilidade

```text
--- Atraso médio por faixa de visibilidade ---
                           mean  median  count        std
faixa_visibilidade                                       
Muito baixa (<5000m)  29.384181    29.0    177  12.991666
Baixa (5000-10000m)   30.053104    30.0   2787  12.323093
Normal (>10000m)      24.371380    23.0    587  14.471169
```

* **mean**: Atraso médio (minutos) para cada faixa.
* **median**: Valor central (menos sensível a outliers).
* **count**: Número de voos na faixa.
* **std**: Desvio padrão – quanto maior, mais dispersos são os atrasos.

**Interpretação**: Voos com visibilidade normal (>10.000m) têm atraso médio de 24,4 min, enquanto os com visibilidade muito baixa (<5.000m) têm 29,4 min – uma diferença de 5 minutos. A faixa intermediária (5.000‑10.000m) apresenta o maior atraso médio (30,1 min), possivelmente por combinar condições adversas sem ainda justificar cancelamentos.

---

## Teste ANOVA (p-value)

```text
ANOVA p-value: 0.0000 (significativo se p < 0.05)
```

* **Definição**: O *p-value* (0,0000) é a probabilidade de as diferenças entre as médias dos grupos serem devidas ao acaso.
* **Conclusão**: Como é menor que 0,05, rejeita‑se a hipótese de que todas as médias são iguais. Portanto, a visibilidade influencia significativamente o atraso.

---

## Correlação Precipitação vs Cancelamentos

```text
--- Correlação precipitação acumulada vs cancelamentos ---
r = 0.018, p = 0.8064
```

* **r (coeficiente de Pearson)**: 0,018 – praticamente zero, indicando ausência de relação linear entre chuva acumulada e número de cancelamentos.
* **p-value**: 0,8064 – muito acima de 0,05, portanto não há significância estatística.

**Interpretação**: Nos dados analisados, a quantidade de chuva não explica os cancelamentos. Outros fatores (vento, visibilidade, decisões operacionais) podem ser mais relevantes.

---

## Atraso Médio com e sem Chuva por Aeroporto

```text
--- Atraso médio com e sem chuva por aeroporto ---
chuva                 False       True      delta
aeroporto_origem                                 
SBGL              16.179372  28.745877  12.566504
SBGR              18.795181  29.208973  10.413792
```

| Aeroporto Origem | Sem Chuva (`False`) | Com Chuva (`True`) | Diferença (`delta`) |
| :--- | :--- | :--- | :--- |
| **SBGL** | 16,18 min | 28,75 min | +12,57 min |
| **SBGR** | 18,80 min | 29,21 min | +10,41 min |

**Interpretação**: Em ambos os aeroportos, dias chuvosos aumentam o atraso médio em cerca de 10 a 13 minutos. O impacto é ligeiramente maior no SBGL (+12,6 min) do que no SBGR (+10,4 min).

---

## Distribuição de Condições Meteorológicas por Ano

```text
--- Distribuição de condições meteorológicas por ano (julho) ---
condicao_meteorologica  Ceu aberto  Chuva  Chuva intensa
ano                                                     
2023                           290   1240             20
2024                           285   1225             40
2025                           340   1190             20
```

* **Métrica**: Mostra quantas observações de cada condição ocorreram em julho de cada ano.
* **Céu aberto**: Aumentou de 290 (2023) para 340 (2025).
* **Chuva**: Reduziu de 1240 para 1190.
* **Chuva intensa**: Manteve‑se baixa, com 20‑40 ocorrências.

**Interpretação**: Há uma leve tendência de melhora nas condições meteorológicas ao longo dos anos, com menos dias chuvosos em 2025.

---

## Condições Meteorológicas em Atrasos > 30 min

```text
--- Condições meteorológicas em atrasos > 30 min ---
condicao_meteorologica
Chuva       94.888755
Nevoeiro     5.111245
Name: proportion, dtype: float64
```

* **Métrica**: Mostra a proporção (%) de cada condição entre os voos com atraso superior a 30 minutos.
* **Chuva**: 94,9% dos atrasos significativos ocorrem sob chuva.
* **Nevoeiro**: 5,1% (registros com visibilidade muito baixa injetados sinteticamente).

**Interpretação**: A grande maioria dos atrasos prolongados está associada à chuva, confirmando que esse é o principal fator meteorológico que impacta a operação.
