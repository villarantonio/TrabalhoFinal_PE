"""
Análise de Variáveis Qualitativas — Star Dataset
Disciplina: Probabilidade e Estatística A — UFG

Variáveis analisadas:
  - Star color    (qualitativa nominal)
  - Spectral Class (qualitativa ordinal: O, B, A, F, G, K, M)
  - Star type     (qualitativa ordinal: 0–5)
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(__file__))
from criar_variaveis import add_variaveis

# ── Configurações de caminho ──────────────────────────────────────────────────
BASE_DIR   = os.path.join(os.path.dirname(__file__), '..')
DATA_FILE  = os.path.join(BASE_DIR, '6 class csv.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'graficos', 'qualitativas')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mapeamento dos tipos estelares para nomes descritivos
STAR_TYPE_NAMES = {
    0: 'Anã Marrom',
    1: 'Anã Vermelha',
    2: 'Anã Branca',
    3: 'Seq. Principal',
    4: 'Supergigante',
    5: 'Hipergigante',
}

# Paleta de 6 cores consistente com os outros scripts
PALETTE = sns.color_palette('tab10', 6)

# ── Carregamento e preparo dos dados ─────────────────────────────────────────
df = pd.read_csv(DATA_FILE)
df['Star type label'] = df['Star type'].map(STAR_TYPE_NAMES)
df = add_variaveis(df)


# ── Padronização de Star color ────────────────────────────────────────────────
# O dataset tem variantes de capitalização e grafia para a mesma cor (ex: "Blue White",
# "blue white", "Blue white", "Blue-white"). Unificamos em categorias canônicas.

def padronizar_cor(cor: str) -> str:
    c = cor.strip().lower()
    if c in ('blue',):
        return 'Blue'
    if c in ('blue white', 'blue-white', 'blue white '):
        return 'Blue White'
    if c in ('red', 'red '):
        return 'Red'
    if c in ('yellow white', 'yellow-white', 'yellowish white',
             'pale yellow orange', 'yellow'):
        return 'Yellow/White'
    if c in ('white', 'whitish'):
        return 'White'
    if c in ('orange', 'orange-red'):
        return 'Orange/Red'
    return cor.strip().title()


df['Star color std'] = df['Star color'].apply(padronizar_cor)


# ── Função: tabela de frequências genérica ────────────────────────────────────
def tabela_frequencias(series: pd.Series, nome: str,
                       ordem: list = None, acumulada: bool = True) -> pd.DataFrame:
    """Retorna e imprime tabela com freq. absoluta, relativa, acumuladas."""
    contagem = series.value_counts()
    if ordem:
        contagem = contagem.reindex(
            [o for o in ordem if o in contagem.index], fill_value=0
        )
    total = len(series)
    freq_rel   = (contagem / total * 100).round(2)
    freq_acum  = contagem.cumsum()
    frel_acum  = freq_rel.cumsum().round(2)

    dados = {
        'Categoria':          contagem.index,
        'Freq. Absoluta':     contagem.values,
        'Freq. Relativa (%)': freq_rel.values,
    }
    if acumulada:
        dados['Freq. Abs. Acumulada']   = freq_acum.values
        dados['Freq. Rel. Acumulada (%)'] = frel_acum.values

    tabela = pd.DataFrame(dados)

    print(f'\n{"="*65}')
    print(f'  Tabela de Frequências — {nome}')
    print(f'{"="*65}')
    print(tabela.to_string(index=False))
    return tabela


# ══════════════════════════════════════════════════════════════════════════════
# 1. STAR COLOR
# ══════════════════════════════════════════════════════════════════════════════
tabela_cor = tabela_frequencias(df['Star color std'], 'Star color (padronizado)', acumulada=False)

# — Gráfico de barras —
cores_ord = df['Star color std'].value_counts()
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(cores_ord.index, cores_ord.values,
       color=sns.color_palette('Set2', len(cores_ord)))
ax.set_title('Distribuição de Star Color', fontsize=14)
ax.set_xlabel('Cor da Estrela')
ax.set_ylabel('Frequência Absoluta')
ax.tick_params(axis='x', rotation=25)
for i, v in enumerate(cores_ord.values):
    ax.text(i, v + 0.4, str(v), ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'barras_star_color.png'), dpi=150)
plt.close()

# — Gráfico de pizza: top 5 + "Outros" —
top5   = cores_ord.head(5)
outros = cores_ord.iloc[5:].sum()
pie_labels = list(top5.index)
pie_values = list(top5.values)
if outros > 0:
    pie_labels.append('Outros')
    pie_values.append(outros)

fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(pie_values, labels=pie_labels, autopct='%1.1f%%',
       colors=sns.color_palette('Set2', len(pie_labels)), startangle=140)
ax.set_title('Proporção das Cores Estelares (Top 5 + Outros)', fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'pizza_star_color.png'), dpi=150)
plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 2. SPECTRAL CLASS
# ══════════════════════════════════════════════════════════════════════════════
# Ordem canônica da sequência espectral (O → M: temperatura decrescente)
ORDEM_SPECTRAL = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
tabela_spec = tabela_frequencias(
    df['Spectral Class'], 'Spectral Class', ordem=ORDEM_SPECTRAL
)

spec_ord = df['Spectral Class'].value_counts().reindex(ORDEM_SPECTRAL, fill_value=0)
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(spec_ord.index, spec_ord.values,
       color=sns.color_palette('coolwarm', len(spec_ord)))
ax.set_title('Distribuição das Classes Espectrais', fontsize=14)
ax.set_xlabel('Classe Espectral')
ax.set_ylabel('Frequência Absoluta')
for i, v in enumerate(spec_ord.values):
    ax.text(i, v + 0.4, str(v), ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'barras_spectral_class.png'), dpi=150)
plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# 3. STAR TYPE
# ══════════════════════════════════════════════════════════════════════════════
ORDEM_TIPOS = list(STAR_TYPE_NAMES.values())
tabela_type = tabela_frequencias(
    df['Star type label'], 'Star type', ordem=ORDEM_TIPOS
)

type_ord = (
    df['Star type label']
    .value_counts()
    .reindex(ORDEM_TIPOS, fill_value=0)
)
fig, ax = plt.subplots(figsize=(10, 5))
barras = ax.bar(type_ord.index, type_ord.values, color=PALETTE)
ax.set_title('Distribuição dos Tipos Estelares', fontsize=14)
ax.set_xlabel('Tipo Estelar')
ax.set_ylabel('Frequência Absoluta')
ax.tick_params(axis='x', rotation=20)
for i, v in enumerate(type_ord.values):
    ax.text(i, v + 0.4, str(v), ha='center', fontsize=9)

# Legenda com cor por tipo (reaproveitada nos outros scripts)
handles = [plt.Rectangle((0, 0), 1, 1, color=PALETTE[i]) for i in range(6)]
ax.legend(handles, ORDEM_TIPOS, title='Tipo Estelar',
          bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'barras_star_type.png'), dpi=150)
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 4. IS_GIANT
# ══════════════════════════════════════════════════════════════════════════════
giant_series = df['is_Giant'].map({0: 'Não Gigante', 1: 'Gigante'})
tabela_giant = tabela_frequencias(giant_series, 'is_Giant (Gigante vs Não Gigante)', acumulada=False)

giant_ord = giant_series.value_counts().reindex(['Gigante', 'Não Gigante'], fill_value=0)
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(giant_ord.index, giant_ord.values,
       color=sns.color_palette('Set2', 2))
ax.set_title('Distribuição de is_Giant', fontsize=14)
ax.set_xlabel('Categoria')
ax.set_ylabel('Frequência Absoluta')
for i, v in enumerate(giant_ord.values):
    ax.text(i, v + 0.4, str(v), ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'barras_is_giant.png'), dpi=150)
plt.close()

print(f'\nGráficos salvos em: {OUTPUT_DIR}')
