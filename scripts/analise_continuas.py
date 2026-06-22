"""
Análise de Variáveis Contínuas — Star Dataset
Disciplina: Probabilidade e Estatística A — UFG

Variáveis analisadas:
  - Luminosity(L/Lo)      → escala original e log₁₀
  - Radius(R/Ro)          → escala original e log₁₀
  - Absolute magnitude(Mv)→ escala original

Para cada variável:
  - Tabela de frequências com densidade
  - Histograma com curva KDE
  - Boxplot por tipo estelar
  - Medidas descritivas no terminal
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
OUTPUT_DIR = os.path.join(BASE_DIR, 'graficos', 'continuas')
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

# ── Carregamento e preparo dos dados ─────────────────────────────────────────
df = pd.read_csv(DATA_FILE)
df['Star type label'] = df['Star type'].map(STAR_TYPE_NAMES)

# Substituir zeros por NaN antes do log para evitar -inf (log(0) indefinido)
df['Luminosity(L/Lo)'] = df['Luminosity(L/Lo)'].replace(0, np.nan)
df['Radius(R/Ro)']     = df['Radius(R/Ro)'].replace(0, np.nan)

# Colunas transformadas em log₁₀
df['log_Luminosity'] = np.log10(df['Luminosity(L/Lo)'])
df['log_Radius']     = np.log10(df['Radius(R/Ro)'])


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def medidas_descritivas(series: pd.Series, nome: str) -> None:
    """Calcula e imprime medidas descritivas de uma série numérica."""
    s = series.dropna()
    media     = s.mean()
    mediana   = s.median()
    moda      = s.mode().iloc[0] if len(s.mode()) > 0 else np.nan
    desvio    = s.std()
    variancia = s.var()
    # CV só faz sentido para escala de razão (média ≠ 0)
    cv        = (desvio / media * 100) if media != 0 else np.nan
    minimo    = s.min()
    maximo    = s.max()
    amplitude = maximo - minimo
    q1        = s.quantile(0.25)
    q3        = s.quantile(0.75)
    iiq       = q3 - q1
    # Assimetria de Pearson (2ª fórmula): positiva = cauda direita
    assimetria = 3 * (media - mediana) / desvio if desvio != 0 else np.nan
    # Curtose de Fisher: 0 = normal, >0 = leptocúrtica, <0 = platicúrtica
    curtose   = stats.kurtosis(s, fisher=True)

    print(f'\n{"="*55}')
    print(f'  Medidas Descritivas — {nome}')
    print(f'{"="*55}')
    print(f'  {"Média:":<35} {media:>15.4f}')
    print(f'  {"Mediana:":<35} {mediana:>15.4f}')
    print(f'  {"Moda:":<35} {moda:>15.4f}')
    print(f'  {"Desvio Padrão:":<35} {desvio:>15.4f}')
    print(f'  {"Variância:":<35} {variancia:>15.4f}')
    print(f'  {"Coef. de Variação (%):":<35} {cv:>15.2f}')
    print(f'  {"Mínimo:":<35} {minimo:>15.4f}')
    print(f'  {"Máximo:":<35} {maximo:>15.4f}')
    print(f'  {"Amplitude:":<35} {amplitude:>15.4f}')
    print(f'  {"Q1 (25%):":<35} {q1:>15.4f}')
    print(f'  {"Q3 (75%):":<35} {q3:>15.4f}')
    print(f'  {"IIQ (Q3 − Q1):":<35} {iiq:>15.4f}')
    print(f'  {"Assimetria de Pearson:":<35} {assimetria:>15.4f}')
    print(f'  {"Curtose (excesso Fisher):":<35} {curtose:>15.4f}')


def tabela_frequencias(series: pd.Series, nome: str,
                       n_classes: int = 6) -> None:
    """Constrói e imprime tabela de frequências com densidade para variável contínua."""
    s = series.dropna()
    contagens, bordas = np.histogram(s, bins=n_classes)
    total    = contagens.sum()
    largura  = bordas[1:] - bordas[:-1]
    # Densidade: freq. relativa / largura da classe — área total = 1
    densidade = contagens / (total * largura)
    freq_rel  = (contagens / total * 100).round(2)
    freq_acum = contagens.cumsum()
    frel_acum = freq_rel.cumsum().round(2)

    intervalos = [
        f'[{bordas[i]:.3g}, {bordas[i+1]:.3g})'
        for i in range(len(contagens))
    ]
    tabela = pd.DataFrame({
        'Intervalo':                intervalos,
        'Freq. Absoluta':           contagens,
        'Freq. Relativa (%)':       freq_rel,
        'Freq. Abs. Acumulada':     freq_acum,
        'Freq. Rel. Acumulada (%)': frel_acum,
        'Densidade':                densidade.round(6),
    })

    print(f'\n{"="*85}')
    print(f'  Tabela de Frequências — {nome}')
    print(f'{"="*85}')
    print(tabela.to_string(index=False))


def histograma_kde(series: pd.Series, nome: str,
                   arquivo: str, xlabel: str) -> None:
    """Histograma normalizado (densidade) com curva KDE sobreposta."""
    s = series.dropna()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(s, ax=ax, kde=True, color='steelblue',
                 edgecolor='white', stat='density', bins=30)
    ax.set_title(f'Histograma com KDE — {nome}', fontsize=13)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Densidade')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, arquivo), dpi=150)
    plt.close()


def boxplot_por_tipo(df: pd.DataFrame, col: str, nome: str,
                     arquivo: str, ylabel: str) -> None:
    """Boxplot da variável `col` separado por tipo estelar."""
    fig, ax = plt.subplots(figsize=(10, 5))
    dados = [
        df[df['Star type'] == t][col].dropna().values
        for t in STAR_TYPE_NAMES
    ]
    bplot = ax.boxplot(dados, patch_artist=True, vert=True)
    for patch, color in zip(bplot['boxes'], PALETTE):
        patch.set_facecolor(color)
    ax.set_xticklabels(list(STAR_TYPE_NAMES.values()), rotation=20, ha='right')
    ax.set_title(f'Boxplot por Tipo Estelar — {nome}', fontsize=13)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, arquivo), dpi=150)
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISES
# ══════════════════════════════════════════════════════════════════════════════

# ── Luminosity — escala original ──────────────────────────────────────────────
print('\n' + '▓'*70)
print('  LUMINOSIDADE (L/Lo) — escala original')
print('▓'*70)
tabela_frequencias(df['Luminosity(L/Lo)'],  'Luminosity (L/Lo)')
medidas_descritivas(df['Luminosity(L/Lo)'], 'Luminosity (L/Lo)')
histograma_kde(df['Luminosity(L/Lo)'],
               'Luminosity (L/Lo)', 'hist_luminosity.png', 'Luminosidade (L/Lo)')
boxplot_por_tipo(df, 'Luminosity(L/Lo)',
                 'Luminosity (L/Lo)', 'boxplot_luminosity.png', 'Luminosidade (L/Lo)')

# ── Luminosity — log₁₀ ────────────────────────────────────────────────────────
# A escala log lineariza a distribuição fortemente assimétrica da luminosidade
print('\n' + '▓'*70)
print('  log₁₀(LUMINOSIDADE) — escala logarítmica')
print('▓'*70)
tabela_frequencias(df['log_Luminosity'],  'log₁₀(Luminosity)')
medidas_descritivas(df['log_Luminosity'], 'log₁₀(Luminosity)')
histograma_kde(df['log_Luminosity'],
               'log₁₀(Luminosity)', 'hist_log_luminosity.png', 'log₁₀(Luminosidade)')
boxplot_por_tipo(df, 'log_Luminosity',
                 'log₁₀(Luminosity)', 'boxplot_log_luminosity.png', 'log₁₀(Luminosidade)')

# ── Radius — escala original ──────────────────────────────────────────────────
print('\n' + '▓'*70)
print('  RAIO (R/Ro) — escala original')
print('▓'*70)
tabela_frequencias(df['Radius(R/Ro)'],  'Radius (R/Ro)')
medidas_descritivas(df['Radius(R/Ro)'], 'Radius (R/Ro)')
histograma_kde(df['Radius(R/Ro)'],
               'Radius (R/Ro)', 'hist_radius.png', 'Raio (R/Ro)')
boxplot_por_tipo(df, 'Radius(R/Ro)',
                 'Radius (R/Ro)', 'boxplot_radius.png', 'Raio (R/Ro)')

# ── Radius — log₁₀ ────────────────────────────────────────────────────────────
print('\n' + '▓'*70)
print('  log₁₀(RAIO) — escala logarítmica')
print('▓'*70)
tabela_frequencias(df['log_Radius'],  'log₁₀(Radius)')
medidas_descritivas(df['log_Radius'], 'log₁₀(Radius)')
histograma_kde(df['log_Radius'],
               'log₁₀(Radius)', 'hist_log_radius.png', 'log₁₀(Raio)')
boxplot_por_tipo(df, 'log_Radius',
                 'log₁₀(Radius)', 'boxplot_log_radius.png', 'log₁₀(Raio)')

# ── Absolute magnitude (Mv) ───────────────────────────────────────────────────
# Magnitude: escala invertida — valores menores = estrelas mais brilhantes
print('\n' + '▓'*70)
print('  MAGNITUDE ABSOLUTA (Mv)')
print('▓'*70)
tabela_frequencias(df['Absolute magnitude(Mv)'],  'Absolute Magnitude (Mv)')
medidas_descritivas(df['Absolute magnitude(Mv)'], 'Absolute Magnitude (Mv)')
histograma_kde(df['Absolute magnitude(Mv)'],
               'Absolute Magnitude (Mv)', 'hist_magnitude.png', 'Magnitude Absoluta (Mv)')
boxplot_por_tipo(df, 'Absolute magnitude(Mv)',
                 'Absolute Magnitude (Mv)', 'boxplot_magnitude.png', 'Magnitude Absoluta (Mv)')

print(f'\nGráficos salvos em: {OUTPUT_DIR}')
