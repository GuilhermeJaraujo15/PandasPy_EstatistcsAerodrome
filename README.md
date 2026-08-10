# Análise de Dados de Voos e Meteorologia

Este projeto realiza uma análise exploratória de dados (EDA) para responder a perguntas de negócio sobre a relação entre condições meteorológicas e operações de voos. Utiliza Python com as bibliotecas Pandas, NumPy, Matplotlib, Seaborn e SciPy para processar e analisar dados de voos (três anos, mês de julho) e dados meteorológicos correspondentes.

---

## Organização dos Dados

O sistema espera **6 arquivos CSV**:

| Arquivo | Descrição | Colunas principais |
| :--- | :--- | :--- |
| `voos_2023.csv` | Voos realizados em julho/2023 | `id_voo`, `aeroporto_origem`, `data`, `horario_previsto`, `status`, `atraso_minutos`, `cancelado`, `motivo_atraso` |
| `voos_2024.csv` | Voos realizados em julho/2024 | *(mesma estrutura)* |
| `voos_2025.csv` | Voos realizados em julho/2025 | *(mesma estrutura)* |
| `meteorologia_aeroportos_2023.csv` | Dados meteorológicos horários para julho/2023 | `id_registro_meteo`, `aeroporto`, `data_hora`, `temperatura_c`, `pressao_hpa`, `visibilidade_m`, `vento_kmh`, `rajada_kmh`, `precipitacao_mm`, `cobertura_nuvens_pct`, `condicao_meteorologica` |
| `meteorologia_aeroportos_2024.csv` | Dados meteorológicos para julho/2024 | *(mesma estrutura)* |
| `meteorologia_aeroportos_2025.csv` | Dados meteorológicos para julho/2025 | *(mesma estrutura)* |


---

## Tecnologias Utilizadas

| Ferramenta | Função |
| :--- | :--- |
| **Python 3.12+** | Linguagem base |
| **Pandas** | Manipulação e integração de dados (merge, agregação, transformações) |
| **NumPy** | Operações vetorizadas e geração de dados sintéticos (para simular baixa visibilidade) |
| **Matplotlib** | Criação e salvamento de gráficos |
| **Seaborn** | Gráficos estatísticos com estética aprimorada |
| **SciPy** | Teste ANOVA e correlação de Pearson |
| **os** | Criação de diretórios (pasta `img/`) |
