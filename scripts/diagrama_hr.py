"""
Diagrama de Hertzsprung-Russell (HR)
Disciplina: Probabilidade e Estatística A — UFG

Eixo X : Temperature (K) — escala log, invertida (temperatura decresce E→D)
Eixo Y : log₁₀(Luminosidade / L☉)
Cor    : tipo estelar (paleta tab10 consistente com os demais scripts)
Tamanho: proporcional ao Radius(R/Ro), normalizado entre 20 e 300 pts²
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── Configurações de caminho ──────────────────────────────────────────────────
BASE_DIR   = os.path.join(os.path.dirname(__file__), '..')
DATA_FILE  = os.path.join(BASE_DIR, '6 class csv.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'graficos')
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

# log₁₀(Luminosidade) — zeros viram NaN antes do log
df['log_Luminosity'] = np.log10(df['Luminosity(L/Lo)'].replace(0, np.nan))

# Normalizar raio para tamanho de ponto entre 20 e 300 pts²
raio = df['Radius(R/Ro)'].fillna(df['Radius(R/Ro)'].median())
r_min, r_max = raio.min(), raio.max()
raio_norm = 20 + 280 * (raio - r_min) / (r_max - r_min)


# ══════════════════════════════════════════════════════════════════════════════
# DIAGRAMA HR
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))

for i, (tipo, nome) in enumerate(STAR_TYPE_NAMES.items()):
    mask = df['Star type'] == tipo
    ax.scatter(
        df.loc[mask, 'Temperature (K)'],
        df.loc[mask, 'log_Luminosity'],
        s=raio_norm[mask],
        color=PALETTE[i],
        label=nome,
        alpha=0.80,
        edgecolors='k',
        linewidths=0.3,
    )

# Temperatura no eixo X em escala log e invertida (conveção astronômica)
ax.set_xscale('log')
ax.invert_xaxis()

ax.set_title('Diagrama de Hertzsprung-Russell', fontsize=15, fontweight='bold')
ax.set_xlabel('Temperatura Efetiva (K)  [escala log, decrescente]', fontsize=12)
ax.set_ylabel('log₁₀(Luminosidade / L☉)', fontsize=12)

ax.legend(title='Tipo Estelar', bbox_to_anchor=(1.01, 1), loc='upper left')

# Anotação explicando o tamanho dos pontos
ax.annotate('● Tamanho ∝ Raio (R/R☉)', xy=(0.02, 0.04),
            xycoords='axes fraction', fontsize=9, color='gray')

plt.tight_layout()
saida = os.path.join(OUTPUT_DIR, 'diagrama_hr.png')
plt.savefig(saida, dpi=150)
plt.close()

print(f'Diagrama HR salvo em: {saida}')
