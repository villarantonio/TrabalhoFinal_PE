"""
Análise de Variável Discreta — Temperature (K)
Disciplina: Probabilidade e Estatística A — UFG

Etapas:
  1. Categorização por intervalos da classificação espectral (6 faixas)
  2. Tabela de frequências completa
  3. Histograma + polígono de frequências (2 subplots)
  4. Medidas descritivas no terminal
  5. Boxplot geral + por tipo estelar (2 subplots)
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ── Configurações de caminho ──────────────────────────────────────────────────
BASE_DIR   = os.path.join(os.path.dirname(__file__), '..')
DATA_FILE  = os.path.join(BASE_DIR, '6 class csv.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'graficos', 'discreta')
os.makedirs(OUTPUT_DIR, exist_ok=True)

STAR_TYPE_NAMES = {
    0: 'Anã Marrom',
    1: 'Anã Vermelha',
    2: 'Anã Branca',
    3: 'Seq. Principal',
    4: 'Supergigante',
    5: 'Hipergigante',
}
PALETTE = sns.color_palette('tab10', 6)

# ── Carregamento dos dados ────────────────────────────────────────────────────
df = pd.read_csv(DATA_FILE)
df['Star type label'] = df['Star type'].map(STAR_TYPE_NAMES)
temp = df['Temperature (K)']


# ══════════════════════════════════════════════════════════════════════════════
# 1. CATEGORIZAÇÃO POR FAIXA ESPECTRAL
# ══════════════════════════════════════════════════════════════════════════════
# Intervalos inspirados nos limites de temperatura das classes espectrais (OBAFGKM).
# right=False: intervalo fechado à esquerda, ex: [3500, 5200)

BINS   = [0, 3500, 5200, 6000, 7500, 30000, float('inf')]
LABELS = [
    'Muito Fria (<3500 K)',
    'Fria (3500–5200 K)',
    'Morna (5200–6000 K)',
    'Moderada (6000–7500 K)',
    'Quente (7500–30000 K)',
    'Muito Quente (>30000 K)',
]

df['Temp Categoria'] = pd.cut(temp, bins=BINS, labels=LABELS, right=False)


# ══════════════════════════════════════════════════════════════════════════════
# 2. TABELA DE FREQUÊNCIAS
# ══════════════════════════════════════════════════════════════════════════════
freq_abs  = df['Temp Categoria'].value_counts().reindex(LABELS)
total     = len(df)
freq_rel  = (freq_abs / total * 100).round(2)
freq_acum = freq_abs.cumsum()
frel_acum = freq_rel.cumsum().round(2)

tabela = pd.DataFrame({
    'Categoria':                LABELS,
    'Freq. Absoluta':           freq_abs.values,
    'Freq. Relativa (%)':       freq_rel.values,
    'Freq. Abs. Acumulada':     freq_acum.values,
    'Freq. Rel. Acumulada (%)': frel_acum.values,
})

print('\n' + '='*75)
print('  Tabela de Frequências — Temperature (K) por Faixa Espectral')
print('='*75)
print(tabela.to_string(index=False))


# ══════════════════════════════════════════════════════════════════════════════
# 3. MEDIDAS DESCRITIVAS
# ══════════════════════════════════════════════════════════════════════════════
media    = temp.mean()
mediana  = temp.median()
moda     = temp.mode().iloc[0]
desvio   = temp.std()
variancia = temp.var()
cv       = desvio / media * 100           # coeficiente de variação em %
minimo   = temp.min()
maximo   = temp.max()
amplitude = maximo - minimo
q1       = temp.quantile(0.25)
q3       = temp.quantile(0.75)
iiq      = q3 - q1
# Assimetria de Pearson: positiva → cauda à direita; negativa → cauda à esquerda
assimetria = 3 * (media - mediana) / desvio
# Curtose de Fisher (excesso): 0 = normal, >0 = leptocúrtica, <0 = platicúrtica
curtose  = stats.kurtosis(temp, fisher=True)

print('\n' + '='*55)
print('  Medidas Descritivas — Temperature (K)')
print('='*55)
print(f'  {"Média:":<35} {media:>12.2f} K')
print(f'  {"Mediana:":<35} {mediana:>12.2f} K')
print(f'  {"Moda:":<35} {moda:>12.2f} K')
print(f'  {"Desvio Padrão:":<35} {desvio:>12.2f} K')
print(f'  {"Variância:":<35} {variancia:>12.2f} K²')
print(f'  {"Coef. de Variação:":<35} {cv:>11.2f} %')
print(f'  {"Mínimo:":<35} {minimo:>12.2f} K')
print(f'  {"Máximo:":<35} {maximo:>12.2f} K')
print(f'  {"Amplitude:":<35} {amplitude:>12.2f} K')
print(f'  {"Q1 (25%):":<35} {q1:>12.2f} K')
print(f'  {"Q3 (75%):":<35} {q3:>12.2f} K')
print(f'  {"IIQ (Q3 - Q1):":<35} {iiq:>12.2f} K')
print(f'  {"Assimetria de Pearson:":<35} {assimetria:>12.4f}')
print(f'  {"Curtose (excesso Fisher):":<35} {curtose:>12.4f}')


# ══════════════════════════════════════════════════════════════════════════════
# 4. HISTOGRAMA + POLÍGONO DE FREQUÊNCIAS
# ══════════════════════════════════════════════════════════════════════════════
N_BINS = 30   # número de classes para o histograma

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# — Subplot 1: Histograma —
contagens, bordas, _ = ax1.hist(
    temp, bins=N_BINS, color='steelblue', edgecolor='white', alpha=0.85
)
ax1.set_title('Histograma — Temperature (K)', fontsize=13)
ax1.set_xlabel('Temperatura (K)')
ax1.set_ylabel('Frequência Absoluta')

# — Subplot 2: Polígono de frequências —
# Ponto médio de cada classe do histograma = ponto de referência do polígono
midpoints = (bordas[:-1] + bordas[1:]) / 2
# Zeros nas extremidades para fechar o polígono (frequência = 0 além dos dados)
x_poly = np.concatenate([[bordas[0]], midpoints, [bordas[-1]]])
y_poly = np.concatenate([[0], contagens, [0]])
ax2.plot(x_poly, y_poly, color='darkorange', linewidth=2, marker='o', markersize=4)
ax2.fill_between(x_poly, y_poly, alpha=0.2, color='darkorange')
ax2.set_title('Polígono de Frequências — Temperature (K)', fontsize=13)
ax2.set_xlabel('Temperatura (K)')
ax2.set_ylabel('Frequência Absoluta')

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, 'histograma_poligono_temperatura.png'), dpi=150
)
plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 5. BOXPLOT GERAL + POR TIPO ESTELAR
# ══════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# — Subplot 1: Boxplot geral —
ax1.boxplot(
    temp, vert=True, patch_artist=True,
    boxprops=dict(facecolor='steelblue', color='navy'),
    medianprops=dict(color='red', linewidth=2),
)
ax1.set_title('Boxplot Geral — Temperature (K)', fontsize=13)
ax1.set_ylabel('Temperatura (K)')
ax1.set_xticks([1])
ax1.set_xticklabels(['Temperature'])

# — Subplot 2: Boxplot por tipo estelar —
dados_por_tipo = [
    df[df['Star type'] == t]['Temperature (K)'].values
    for t in STAR_TYPE_NAMES
]
bplot = ax2.boxplot(dados_por_tipo, patch_artist=True, vert=True)
for patch, color in zip(bplot['boxes'], PALETTE):
    patch.set_facecolor(color)
ax2.set_xticklabels(list(STAR_TYPE_NAMES.values()), rotation=20, ha='right')
ax2.set_title('Boxplot por Tipo Estelar — Temperature (K)', fontsize=13)
ax2.set_ylabel('Temperatura (K)')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'boxplot_temperatura.png'), dpi=150)
plt.close()

# ── Separatrizes por tipo estelar — Temperature (K) ──────────────────────────
GRAFICOS_DIR = os.path.join(BASE_DIR, 'graficos')
rows = []
for t, nome in STAR_TYPE_NAMES.items():
    s = df[df['Star type'] == t]['Temperature (K)']
    q1_, q3_ = s.quantile(0.25), s.quantile(0.75)
    rows.append({'Tipo': nome, 'Q1': q1_, 'Mediana': s.median(), 'Q3': q3_, 'IIQ': q3_ - q1_})
sep_temp = pd.DataFrame(rows)
print('\n' + '='*60)
print('  Separatrizes por Tipo Estelar — Temperature (K)')
print('='*60)
print(sep_temp.to_string(index=False))
sep_temp.to_csv(os.path.join(GRAFICOS_DIR, 'separatrizes_temperatura.csv'), index=False)

print(f'\nGráficos salvos em: {OUTPUT_DIR}')
