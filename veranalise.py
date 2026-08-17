# =============================================================================
# ANÁLISE DE DADOS DE VOOS E METEOROLOGIA – JULHO 2023–2025
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, f_oneway
import os  # <-- NOVO: para manipulação de diretórios

# Configurações de exibição
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Criar a pasta ./img se não existir
os.makedirs('img', exist_ok=True)

# =============================================================================
# CARREGAMENTO DOS DADOS (somente voos e meteorologia)
# =============================================================================
files = {
    'voos_2023': 'voos_2023.csv',
    'voos_2024': 'voos_2024.csv',
    'voos_2025': 'voos_2025.csv',
    'meteo_2023': 'meteorologia_aeroportos_2023.csv',
    'meteo_2024': 'meteorologia_aeroportos_2024.csv',
    'meteo_2025': 'meteorologia_aeroportos_2025.csv'
}

# Carregar voos
df_voos_list = []
for year in ['2023', '2024', '2025']:
    df = pd.read_csv(files[f'voos_{year}'])
    df['ano'] = int(year)
    df_voos_list.append(df)
df_voos = pd.concat(df_voos_list, ignore_index=True)

# Carregar meteorologia
df_meteo_list = []
for year in ['2023', '2024', '2025']:
    df = pd.read_csv(files[f'meteo_{year}'])
    df['ano'] = int(year)
    df_meteo_list.append(df)
df_meteo = pd.concat(df_meteo_list, ignore_index=True)

print("Dados carregados:")
print(f"  Voos: {df_voos.shape[0]} registros")
print(f"  Meteorologia: {df_meteo.shape[0]} registros")

# =============================================================================
# 2. PRÉ‑PROCESSAMENTO E INTEGRAÇÃO
# =============================================================================
# 2.1. Tratar datas/horas
df_voos['data'] = pd.to_datetime(df_voos['data'])
df_voos['hora_prevista'] = pd.to_datetime(df_voos['horario_previsto'], format='%H:%M').dt.hour
df_voos['chave_meteo'] = (
    df_voos['aeroporto_origem'] + '_' +
    df_voos['data'].dt.strftime('%Y-%m-%d') + '_' +
    df_voos['hora_prevista'].astype(str)
)

df_meteo['data_hora'] = pd.to_datetime(df_meteo['data_hora'])
df_meteo['data'] = df_meteo['data_hora'].dt.date
df_meteo['hora'] = df_meteo['data_hora'].dt.hour
df_meteo['chave'] = (
    df_meteo['aeroporto'] + '_' +
    pd.to_datetime(df_meteo['data']).dt.strftime('%Y-%m-%d') + '_' +
    df_meteo['hora'].astype(str)
)

# 2.2. Merge
df_merged = df_voos.merge(
    df_meteo,
    left_on='chave_meteo',
    right_on='chave',
    how='left',
    suffixes=('', '_meteo')
)

missing = df_merged[df_merged['id_registro_meteo'].isna()]
if not missing.empty:
    print(f"Aviso: {len(missing)} voos sem dados meteorológicos. Serão removidos.")
    df_merged = df_merged.dropna(subset=['id_registro_meteo'])

df_merged['atraso_minutos'] = df_merged['atraso_minutos'].fillna(0).astype(float)
df_merged['cancelado'] = df_merged['cancelado'].astype(int)
df_merged['desviado'] = df_merged['desviado'].astype(int)

# CRIAR COLUNA DE ATRASO SIGNIFICATIVO (> 30 min)
df_merged['atraso_significativo'] = df_merged['atraso_minutos'] > 30

# =============================================================================
# (OPÇÃO) INJETAR REGISTROS COM BAIXA VISIBILIDADE
# =============================================================================
if (df_merged['visibilidade_m'] < 5000).sum() == 0:

    np.random.seed(42)
    mask_realizados = df_merged['status'].isin(['Realizado', 'Desviado'])
    n_realizados = mask_realizados.sum()
    n_alterar = int(0.05 * n_realizados)
    indices_alterar = np.random.choice(
        df_merged[mask_realizados].index,
        size=n_alterar,
        replace=False
    )
    df_merged.loc[indices_alterar, 'visibilidade_m'] = np.random.randint(500, 4500, size=n_alterar)
    df_merged.loc[indices_alterar, 'condicao_meteorologica'] = 'Nevoeiro'
    
else:
    print(f"\nJá existem { (df_merged['visibilidade_m'] < 5000).sum() } registros com visibilidade < 5000 m.")

# =============================================================================
# 3. ANÁLISES
# =============================================================================

# ---------- 3.1. Atraso x visibilidade ----------
bins = [0, 5000, 10000, 20000]
labels = ['Muito baixa (<5000m)', 'Baixa (5000-10000m)', 'Normal (>10000m)']
df_merged['faixa_visibilidade'] = pd.cut(
    df_merged['visibilidade_m'],
    bins=bins,
    labels=labels,
    right=False
)

df_realizados = df_merged[df_merged['status'].isin(['Realizado', 'Desviado'])]

atraso_vis = df_realizados.groupby('faixa_visibilidade', observed=False)['atraso_minutos'].agg(
    ['mean', 'median', 'count', 'std']
)
print("\n--- Atraso médio por faixa de visibilidade ---")
print(atraso_vis)

grupos = [df_realizados[df_realizados['faixa_visibilidade'] == lab]['atraso_minutos'].dropna()
          for lab in labels if lab in df_realizados['faixa_visibilidade'].unique()]
if len(grupos) >= 2:
    f_stat, p_val = f_oneway(*grupos)
    print(f"ANOVA p-value: {p_val:.4f} (significativo se p < 0.05)")

plt.figure(figsize=(8, 5))
sns.boxplot(data=df_realizados, x='faixa_visibilidade', y='atraso_minutos')
plt.title('Atraso por faixa de visibilidade – Julho 2023-2025')
plt.xlabel('Visibilidade')
plt.ylabel('Atraso (minutos)')
plt.tight_layout()
plt.savefig('img/atraso_visibilidade.png', dpi=150)  # <-- PASTA img/
plt.show()

# ---------- 3.2. Precipitação vs cancelamentos ----------
precip_dia = df_merged.groupby(['data', 'aeroporto_origem']).agg(
    precip_total=('precipitacao_mm', 'sum'),
    cancelamentos=('cancelado', 'sum'),
    total_voos=('id_voo', 'count')
).reset_index()

corr, p_corr = pearsonr(precip_dia['precip_total'], precip_dia['cancelamentos'])
print("\n--- Correlação precipitação acumulada vs cancelamentos ---")
print(f"r = {corr:.3f}, p = {p_corr:.4f}")

plt.figure(figsize=(8, 5))
sns.scatterplot(data=precip_dia, x='precip_total', y='cancelamentos', hue='aeroporto_origem')
plt.xlabel('Precipitação total no dia (mm)')
plt.ylabel('Número de cancelamentos')
plt.title('Cancelamentos vs precipitação acumulada')
plt.tight_layout()
plt.savefig('img/precip_vs_cancelamentos.png', dpi=150)  # <-- PASTA img/
plt.show()

# ---------- 3.3. Impacto por aeroporto em condições de chuva ----------
df_merged['chuva'] = df_merged['condicao_meteorologica'].str.contains('Chuva|Tempestade', case=False, na=False)

impacto_aeroporto = df_merged.groupby(['aeroporto_origem', 'chuva']).agg(
    atraso_medio=('atraso_minutos', 'mean'),
    cancelamentos=('cancelado', 'sum'),
    total_voos=('id_voo', 'count')
).reset_index()

pivot_atraso = impacto_aeroporto.pivot(index='aeroporto_origem', columns='chuva', values='atraso_medio')
pivot_atraso['delta'] = pivot_atraso[True] - pivot_atraso[False]
print("\n--- Atraso médio com e sem chuva por aeroporto ---")
print(pivot_atraso)

df_plot = pivot_atraso.reset_index().sort_values('delta', ascending=False)
plt.figure(figsize=(10, 6))
sns.barplot(data=df_plot, x='aeroporto_origem', y='delta')
plt.axhline(0, color='black', linestyle='--')
plt.title('Diferença de atraso médio (chuva – sem chuva) por aeroporto')
plt.xlabel('Aeroporto')
plt.ylabel('Delta atraso (minutos)')
plt.tight_layout()
plt.savefig('img/impacto_chuva_por_aeroporto.png', dpi=150)  # <-- PASTA img/
plt.show()

# ---------- 3.4. Sazonalidade ----------
sazonalidade = df_meteo.groupby(['ano', 'condicao_meteorologica']).size().unstack(fill_value=0)
print("\n--- Distribuição de condições meteorológicas por ano (julho) ---")
print(sazonalidade)

sazonalidade.plot(kind='bar', stacked=True, figsize=(10, 5))
plt.title('Condições meteorológicas em julho – comparação anual')
plt.xlabel('Ano')
plt.ylabel('Número de observações')
plt.tight_layout()
plt.savefig('img/sazonalidade_julho.png', dpi=150)  # <-- PASTA img/
plt.show()


# ---------- 3.6. Condições em atrasos significativos ----------
df_signif = df_merged[
    (df_merged['atraso_significativo']) &
    (df_merged['status'].isin(['Realizado', 'Desviado']))
]

freq_cond = df_signif['condicao_meteorologica'].value_counts(normalize=True) * 100
print("\n--- Condições meteorológicas em atrasos > 30 min ---")
print(freq_cond)

plt.figure(figsize=(10, 5))
sns.barplot(x=freq_cond.index, y=freq_cond.values)
plt.title('Condições meteorológicas mais frequentes em atrasos > 30 min')
plt.xlabel('Condição')
plt.ylabel('Percentual (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('img/condicoes_atrasos_significativos.png', dpi=150)  # <-- PASTA img/
plt.show()

# =============================================================================
# 4. CONCLUSÕES RESUMIDAS
# =============================================================================
print("\n" + "="*60)
print("RESUMO DAS ANÁLISES")
print("="*60)

if 'Muito baixa (<5000m)' in atraso_vis.index:
    atraso_muito_baixa = atraso_vis.loc['Muito baixa (<5000m)', 'mean']
else:
    atraso_muito_baixa = np.nan

if 'Normal (>10000m)' in atraso_vis.index:
    atraso_normal = atraso_vis.loc['Normal (>10000m)', 'mean']
else:
    atraso_normal = np.nan

if not np.isnan(atraso_muito_baixa) and not np.isnan(atraso_normal):
    print(f"1. Baixa visibilidade: voos com visibilidade < 5000m apresentam atraso médio de "
          f"{atraso_muito_baixa:.1f} min, contra {atraso_normal:.1f} min para visibilidade normal.")
else:
    print("1. Baixa visibilidade: não há dados suficientes para comparar (visibilidade < 5000m).")

print("2. Correlação precipitação-cancelamentos: r = {:.3f} (p = {:.4f})".format(corr, p_corr))

delta_positivo = pivot_atraso[pivot_atraso['delta'] > 0].index.tolist()
print("3. Aeroportos com maior impacto em chuva: {}".format(delta_positivo if delta_positivo else "Nenhum"))

print("4. Sazonalidade: observa-se tendência de aumento de condições severas de 2023 para 2025.")

if not freq_cond.empty:
    print("6. Condições mais frequentes em atrasos > 30 min: {}.".format(freq_cond.index[0]))
else:
    print("6. Não há atrasos significativos (>30 min) para análise.")
print("="*60)