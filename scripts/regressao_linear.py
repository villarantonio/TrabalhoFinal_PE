"""
Correlação de Pearson e Regressão Linear Simples — Star Dataset
Disciplina: Probabilidade e Estatística A — UFG

Etapas:
  1. Matriz de correlação de Pearson (variáveis numéricas + log-transformadas)
  2. Identificação automática do par com maior |correlação|
  3. Regressão linear simples (scipy.stats.linregress)
  4. Impressão de R², RMSE, coeficientes e interpretação
  5. Gráfico de dispersão com reta ajustada e equação anotada
  6. Gráfico de resíduos vs. valores ajustados
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
OUTPUT_DIR = os.path.join(BASE_DIR, 'graficos', 'regressao')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Carregamento e preparo dos dados ─────────────────────────────────────────
df = pd.read_csv(DATA_FILE)

# Colunas log-transformadas (zeros → NaN antes do log)
df['log_Luminosity'] = np.log10(df['Luminosity(L/Lo)'].replace(0, np.nan))
df['log_Radius']     = np.log10(df['Radius(R/Ro)'].replace(0, np.nan))

# Subconjunto com todas as variáveis numéricas de interesse
NUM_COLS = [
    'Temperature (K)',
    'Luminosity(L/Lo)',
    'Radius(R/Ro)',
    'Absolute magnitude(Mv)',
    'log_Luminosity',
    'log_Radius',
]
df_num = df[NUM_COLS].dropna()


# ══════════════════════════════════════════════════════════════════════════════
# 1. MATRIZ DE CORRELAÇÃO DE PEARSON
# ══════════════════════════════════════════════════════════════════════════════
corr = df_num.corr(method='pearson')

print('\n' + '='*75)
print('  Matriz de Correlação de Pearson')
print('='*75)
print(corr.round(4).to_string())

# Heatmap da correlação
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt='.3f', cmap='coolwarm',
            center=0, square=True, ax=ax, linewidths=0.5,
            annot_kws={'size': 9})
ax.set_title('Matriz de Correlação de Pearson — Star Dataset', fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'heatmap_correlacao.png'), dpi=150)
plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 2. PAR COM MAIOR CORRELAÇÃO ABSOLUTA
# ══════════════════════════════════════════════════════════════════════════════
# Zerar a diagonal para excluir correlação de variável com ela mesma
corr_abs = corr.abs().copy()
np.fill_diagonal(corr_abs.values, 0.0)

# Também zeramos o triângulo superior para não contar cada par duas vezes
for i in range(len(corr_abs.columns)):
    for j in range(i, len(corr_abs.columns)):
        corr_abs.iloc[i, j] = 0.0

idx_max   = corr_abs.stack().idxmax()
var_x, var_y = idx_max          # (linha, coluna) com maior |r|
r_max     = corr.loc[var_x, var_y]

print(f'\n  Par de maior correlação absoluta: "{var_x}"  ×  "{var_y}"')
print(f'  Pearson r = {r_max:.4f}')


# ══════════════════════════════════════════════════════════════════════════════
# 3. REGRESSÃO LINEAR SIMPLES
# ══════════════════════════════════════════════════════════════════════════════
dados_validos = df_num[[var_x, var_y]].dropna()
x = dados_validos[var_x].values
y = dados_validos[var_y].values

# scipy.stats.linregress retorna slope, intercept, r, p-valor e erro padrão do slope
slope, intercept, r_value, p_value, se_slope = stats.linregress(x, y)

y_pred  = slope * x + intercept
residuos = y - y_pred
r2      = r_value ** 2
rmse    = np.sqrt(np.mean(residuos ** 2))

print('\n' + '='*55)
print('  Resultados da Regressão Linear Simples')
print('='*55)
print(f'  {"Variável X (preditora):":<35} {var_x}')
print(f'  {"Variável Y (resposta):":<35} {var_y}')
print(f'  {"Coeficiente angular (b₁):":<35} {slope:>14.6f}')
print(f'  {"Coeficiente linear  (b₀):":<35} {intercept:>14.6f}')
print(f'  {"Correlação de Pearson (r):":<35} {r_value:>14.6f}')
print(f'  {"R² (coef. de determinação):":<35} {r2:>14.6f}')
print(f'  {"RMSE:":<35} {rmse:>14.6f}')
print(f'  {"p-valor:":<35} {p_value:>14.2e}')
# Interpretação: R² representa a fração da variância de Y explicada linearmente por X.
# p-valor < 0.05 indica que o coeficiente angular é estatisticamente significativo.
print(f'\n  Equação ajustada:')
print(f'    ŷ = {slope:.4f} · x  +  ({intercept:.4f})')
print(f'  Interpretação: {r2*100:.1f}% da variância de "{var_y}"')
print(f'  é explicada linearmente por "{var_x}".')


# ══════════════════════════════════════════════════════════════════════════════
# 4. GRÁFICO DE DISPERSÃO COM RETA AJUSTADA
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 6))

ax.scatter(x, y, alpha=0.55, color='steelblue',
           edgecolors='k', linewidths=0.3, label='Observações')

x_line = np.linspace(x.min(), x.max(), 300)
y_line = slope * x_line + intercept
ax.plot(x_line, y_line, color='red', linewidth=2, label='Reta ajustada')

# Anotar equação e R² no canto superior esquerdo
eq_texto = (
    f'ŷ = {slope:.4f} · x  +  ({intercept:.4f})\n'
    f'R² = {r2:.4f}   |   RMSE = {rmse:.4f}'
)
ax.annotate(eq_texto, xy=(0.04, 0.88), xycoords='axes fraction',
            fontsize=9, color='darkred',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85))

ax.set_xlabel(var_x, fontsize=11)
ax.set_ylabel(var_y, fontsize=11)
ax.set_title(f'Regressão Linear Simples\n{var_x}  ×  {var_y}', fontsize=13)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'dispersao_regressao.png'), dpi=150)
plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 5. GRÁFICO DE RESÍDUOS
# ══════════════════════════════════════════════════════════════════════════════
# Resíduos bem comportados (homocedasticidade) devem estar distribuídos
# aleatoriamente em torno de zero, sem padrão sistemático.

fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(y_pred, residuos, alpha=0.55, color='darkorange',
           edgecolors='k', linewidths=0.3)
ax.axhline(0, color='red', linewidth=1.5, linestyle='--', label='Resíduo = 0')
ax.set_xlabel('Valores Ajustados (ŷ)', fontsize=11)
ax.set_ylabel('Resíduos  (y − ŷ)', fontsize=11)
ax.set_title('Gráfico de Resíduos vs. Valores Ajustados', fontsize=13)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'residuos_regressao.png'), dpi=150)
plt.close()

print(f'\nGráficos salvos em: {OUTPUT_DIR}')
