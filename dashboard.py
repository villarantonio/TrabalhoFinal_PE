"""
Dashboard Interativo — Análise Estatística do Star Dataset
Disciplina: Probabilidade e Estatística A — UFG
Grupo: Antonio Henrique, Jamily, Júlia

Execute com:
    streamlit run dashboard.py
"""

import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats as scipy_stats

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Star Dataset — Análise Estatística",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "6 class csv.csv")

# ── Constantes ────────────────────────────────────────────────────────────────
STAR_TYPE_NAMES = {
    0: "Anã Marrom",
    1: "Anã Vermelha",
    2: "Anã Branca",
    3: "Seq. Principal",
    4: "Supergigante",
    5: "Hipergigante",
}
ORDEM_SPECTRAL = ["O", "B", "A", "F", "G", "K", "M"]
PALETTE_6 = px.colors.qualitative.D3[:6]

TEMP_BINS   = [0, 3500, 5200, 6000, 7500, 30000, float("inf")]
TEMP_LABELS = [
    "Muito Fria (<3500 K)",
    "Fria (3500–5200 K)",
    "Morna (5200–6000 K)",
    "Moderada (6000–7500 K)",
    "Quente (7500–30000 K)",
    "Muito Quente (>30000 K)",
]


# ── Carregamento e preparo dos dados ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    # Padronização robusta de Star color
    def padronizar_cor(cor: str) -> str:
        c = cor.strip().lower()
        if c == "blue":
            return "Blue"
        if c in ("blue white", "blue-white", "blue white "):
            return "Blue White"
        if c in ("red", "red "):
            return "Red"
        if c in (
            "yellow white", "yellow-white", "yellowish white",
            "pale yellow orange", "yellow", "white-yellow",
            "yellowish",                        # corrigido: mapeado aqui
        ):
            return "Yellow/White"
        if c in ("white", "whitish"):
            return "White"
        if c in ("orange", "orange-red"):
            return "Orange/Red"
        return cor.strip().title()

    df["Star color std"] = df["Star color"].apply(padronizar_cor)
    df["Star type label"] = df["Star type"].map(STAR_TYPE_NAMES)

    # Log-transformações
    df["log_Luminosity"] = np.log10(df["Luminosity(L/Lo)"].replace(0, np.nan))
    df["log_Radius"]     = np.log10(df["Radius(R/Ro)"].replace(0, np.nan))

    # Faixas de temperatura
    df["Temp Categoria"] = pd.cut(
        df["Temperature (K)"], bins=TEMP_BINS, labels=TEMP_LABELS, right=False
    )

    return df


df = load_data()


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(v, dec=4):
    if pd.isna(v):
        return "—"
    if abs(v) > 1e6 or (abs(v) < 1e-3 and v != 0):
        return f"{v:.{dec}e}"
    return f"{v:,.{dec}f}"


def tabela_freq_qualitativa(series: pd.Series, ordem=None) -> pd.DataFrame:
    contagem = series.value_counts()
    if ordem:
        contagem = contagem.reindex([o for o in ordem if o in contagem.index], fill_value=0)
    total = len(series)
    fr = (contagem / total * 100).round(2)
    return pd.DataFrame({
        "Categoria":                 contagem.index.tolist(),
        "Freq. Absoluta":            contagem.values.tolist(),
        "Freq. Relativa (%)":        fr.values.tolist(),
        "Freq. Abs. Acumulada":      contagem.cumsum().values.tolist(),
        "Freq. Rel. Acumulada (%)":  fr.cumsum().round(2).values.tolist(),
    })


def tabela_freq_continua(series: pd.Series, n_classes: int = 6) -> pd.DataFrame:
    s = series.dropna()
    contagens, bordas = np.histogram(s, bins=n_classes)
    total    = contagens.sum()
    largura  = bordas[1:] - bordas[:-1]
    densidade = contagens / (total * largura)
    freq_rel  = (contagens / total * 100).round(2)
    freq_acum = contagens.cumsum()
    frel_acum = freq_rel.cumsum().round(2)
    def fmt_borda(v: float) -> str:
        if v == 0:
            return "0"
        av = abs(v)
        if av >= 1e6 or av < 1e-2:
            # notação científica legível: 1.42 × 10⁵
            exp = int(np.floor(np.log10(av)))
            mantissa = v / 10**exp
            sup = str(exp).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
            return f"{mantissa:.2f} × 10{sup}"
        if av >= 1000:
            return f"{v:,.2f}"
        return f"{v:.4g}"

    intervalos = [f"[{fmt_borda(bordas[i])}, {fmt_borda(bordas[i+1])})" for i in range(len(contagens))]
    return pd.DataFrame({
        "Intervalo":                intervalos,
        "Freq. Absoluta":           contagens.tolist(),
        "Freq. Relativa (%)":       freq_rel.tolist(),
        "Freq. Abs. Acumulada":     freq_acum.tolist(),
        "Freq. Rel. Acumulada (%)": frel_acum.tolist(),
        "Densidade":                [round(float(d), 6) for d in densidade],
    })


def medidas_descritivas(series: pd.Series) -> dict:
    s = series.dropna()
    media   = s.mean()
    mediana = s.median()
    moda_v  = s.mode().iloc[0] if len(s.mode()) > 0 else np.nan
    desvio  = s.std()
    variancia = s.var()
    cv      = (desvio / media * 100) if media != 0 else np.nan
    q1      = s.quantile(0.25)
    q3      = s.quantile(0.75)
    assim   = 3 * (media - mediana) / desvio if desvio != 0 else np.nan
    curtose = scipy_stats.kurtosis(s, fisher=True)
    return {
        "Média":                    media,
        "Mediana":                  mediana,
        "Moda":                     moda_v,
        "Desvio Padrão":            desvio,
        "Variância":                variancia,
        "Coef. de Variação (%)":    cv,
        "Mínimo":                   s.min(),
        "Máximo":                   s.max(),
        "Amplitude":                s.max() - s.min(),
        "Q1 (25%)":                 q1,
        "Q3 (75%)":                 q3,
        "IIQ (Q3 − Q1)":           q3 - q1,
        "Assimetria de Pearson":    assim,
        "Curtose (Fisher)":         curtose,
    }


def render_medidas(medidas: dict):
    rows = [(k, fmt(v, 4)) for k, v in medidas.items()]
    md_df = pd.DataFrame(rows, columns=["Medida", "Valor"])
    st.dataframe(md_df, use_container_width=True, hide_index=True)


# ── Sidebar — navegação ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("⭐ Star Dataset")
    st.caption("Probabilidade e Estatística A — UFG")
    st.markdown("---")
    secao = st.radio(
        "Navegar para",
        [
            "📋 Visão Geral do Dataset",
            "🏷️ Variáveis Qualitativas",
            "🌡️ Variável Discreta — Temperatura",
            "📊 Variáveis Contínuas",
            "🌌 Diagrama de Hertzsprung-Russell",
            "📈 Correlação e Regressão",
        ],
    )
    st.markdown("---")
    st.markdown(
        "**Grupo:** Antonio Henrique · Jamily · Júlia  \n"
        "**Dataset:** Star Classification (Kaggle)  \n"
        "**Amostras:** 240 estrelas · 6 tipos"
    )


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — VISÃO GERAL DO DATASET
# ══════════════════════════════════════════════════════════════════════════════
if secao == "📋 Visão Geral do Dataset":
    st.header("📋 Visão Geral do Dataset")
    st.markdown(
        "O **Star Classification Dataset** contém medições de **240 estrelas** "
        "distribuídas igualmente entre 6 tipos estelares (40 por tipo), "
        "abrangendo 7 variáveis físicas e de classificação."
    )

    # Descrição das variáveis
    st.subheader("Variáveis do Dataset")
    vars_df = pd.DataFrame([
        ["Temperature (K)",        "Quantitativa Discreta",    "Temperatura superficial em Kelvin"],
        ["Luminosity (L/Lo)",      "Quantitativa Contínua",    "Luminosidade relativa ao Sol"],
        ["Radius (R/Ro)",          "Quantitativa Contínua",    "Raio relativo ao Sol"],
        ["Absolute magnitude(Mv)", "Quantitativa Contínua",    "Magnitude absoluta (escala invertida: menor = mais brilhante)"],
        ["Star type",              "Qualitativa Ordinal",       "Tipo estelar (0=Anã Marrom … 5=Hipergigante)"],
        ["Star color",             "Qualitativa Nominal",       "Cor observada da estrela"],
        ["Spectral Class",         "Qualitativa Ordinal",       "Classe espectral de Morgan-Keenan (O→M)"],
    ], columns=["Variável", "Tipo", "Descrição"])
    st.dataframe(vars_df, use_container_width=True, hide_index=True)

    # Filtros
    st.subheader("Explorar Dados")
    col1, col2, col3 = st.columns(3)
    with col1:
        tipos_sel = st.multiselect(
            "Filtrar por Tipo Estelar",
            options=list(STAR_TYPE_NAMES.values()),
            default=list(STAR_TYPE_NAMES.values()),
        )
    with col2:
        spec_sel = st.multiselect(
            "Filtrar por Classe Espectral",
            options=ORDEM_SPECTRAL,
            default=ORDEM_SPECTRAL,
        )
    with col3:
        n_linhas = st.slider("Número de linhas exibidas", 10, 240, 50)

    mask = (
        df["Star type label"].isin(tipos_sel) &
        df["Spectral Class"].isin(spec_sel)
    )
    df_filtrado = df[mask].head(n_linhas)[[
        "Temperature (K)", "Luminosity(L/Lo)", "Radius(R/Ro)",
        "Absolute magnitude(Mv)", "Star type label", "Star color std", "Spectral Class"
    ]].rename(columns={
        "Star type label": "Tipo Estelar",
        "Star color std":  "Cor (padronizada)",
    })

    st.caption(f"Mostrando {len(df_filtrado)} de {mask.sum()} registros filtrados.")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # Estatísticas rápidas
    st.subheader("Estatísticas Rápidas")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de estrelas", "240")
    c2.metric("Tipos estelares", "6")
    c3.metric("Temperatura mínima", "1.939 K")
    c4.metric("Temperatura máxima", "40.000 K")
    c1b, c2b, c3b, c4b = st.columns(4)
    c1b.metric("Luminosidade mín.", "8×10⁻⁵ L/Lo")
    c2b.metric("Luminosidade máx.", "849.420 L/Lo")
    c3b.metric("Raio mín.", "0,008 R/Ro")
    c4b.metric("Raio máx.", "1.948,5 R/Ro")


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — VARIÁVEIS QUALITATIVAS
# ══════════════════════════════════════════════════════════════════════════════
elif secao == "🏷️ Variáveis Qualitativas":
    st.header("🏷️ Variáveis Qualitativas")
    st.markdown(
        "Três variáveis qualitativas foram analisadas: **Star color** (nominal), "
        "**Spectral Class** (ordinal) e **Star type** (ordinal)."
    )

    aba1, aba2, aba3 = st.tabs(["🎨 Star Color", "🔭 Spectral Class", "⭐ Star Type"])

    # ── Star Color ────────────────────────────────────────────────────────────
    with aba1:
        st.subheader("Cor Estelar (Star Color)")
        st.markdown(
            "Os valores brutos do dataset contêm variações de grafia para a mesma cor "
            "(ex.: `'Blue white'`, `'blue white'`, `'Blue-white'`). "
            "Após padronização, foram definidas **6 categorias canônicas**."
        )

        tabela_cor = tabela_freq_qualitativa(df["Star color std"])

        col_g, col_t = st.columns([3, 2])
        with col_g:
            tipo_grafico = st.radio("Tipo de gráfico", ["Barras", "Pizza"], horizontal=True, key="cor_chart")
            if tipo_grafico == "Barras":
                fig = px.bar(
                    tabela_cor,
                    x="Categoria", y="Freq. Absoluta",
                    text="Freq. Absoluta",
                    color="Categoria",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    title="Distribuição de Star Color",
                    labels={"Categoria": "Cor", "Freq. Absoluta": "Frequência"},
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(showlegend=False, height=420)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.pie(
                    tabela_cor,
                    names="Categoria", values="Freq. Absoluta",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    title="Proporção das Cores Estelares",
                )
                fig.update_traces(textinfo="label+percent")
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        with col_t:
            st.markdown("**Tabela de Frequências**")
            st.dataframe(tabela_cor, use_container_width=True, hide_index=True)

    # ── Spectral Class ────────────────────────────────────────────────────────
    with aba2:
        st.subheader("Classe Espectral (Spectral Class)")
        st.markdown(
            "Sequência de Morgan-Keenan em ordem de temperatura decrescente: "
            "**O → B → A → F → G → K → M**. "
            "Destaque para a alta concentração em M (estrelas frias) e O (estrelas muito quentes)."
        )

        tabela_spec = tabela_freq_qualitativa(df["Spectral Class"], ordem=ORDEM_SPECTRAL)

        col_g, col_t = st.columns([3, 2])
        with col_g:
            coolwarm = ["#3b4cc0","#688aef","#99badd","#c9d8ef","#edd1c2","#f7a789","#d65f5f"]
            fig = px.bar(
                tabela_spec,
                x="Categoria", y="Freq. Absoluta",
                text="Freq. Absoluta",
                color="Categoria",
                color_discrete_sequence=coolwarm,
                title="Distribuição das Classes Espectrais",
                labels={"Categoria": "Classe Espectral", "Freq. Absoluta": "Frequência"},
                category_orders={"Categoria": ORDEM_SPECTRAL},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, height=420)
            st.plotly_chart(fig, use_container_width=True)
        with col_t:
            st.markdown("**Tabela de Frequências**")
            st.dataframe(tabela_spec, use_container_width=True, hide_index=True)

        st.info(
            "**Nota:** A classe G tem apenas 1 observação no dataset. "
            "Isso reflete um desequilíbrio natural da amostra, não um erro."
        )

    # ── Star Type ─────────────────────────────────────────────────────────────
    with aba3:
        st.subheader("Tipo Estelar (Star Type)")
        st.markdown(
            "Dataset **perfeitamente balanceado**: 40 observações por tipo estelar. "
            "Star type é uma variável ordinal com escala 0–5."
        )

        ordem_tipos = list(STAR_TYPE_NAMES.values())
        tabela_type = tabela_freq_qualitativa(df["Star type label"], ordem=ordem_tipos)

        col_g, col_t = st.columns([3, 2])
        with col_g:
            fig = px.bar(
                tabela_type,
                x="Categoria", y="Freq. Absoluta",
                text="Freq. Absoluta",
                color="Categoria",
                color_discrete_sequence=PALETTE_6,
                title="Distribuição dos Tipos Estelares",
                labels={"Categoria": "Tipo Estelar", "Freq. Absoluta": "Frequência"},
                category_orders={"Categoria": ordem_tipos},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, height=420)
            st.plotly_chart(fig, use_container_width=True)
        with col_t:
            st.markdown("**Tabela de Frequências**")
            st.dataframe(tabela_type, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — VARIÁVEL DISCRETA (TEMPERATURA)
# ══════════════════════════════════════════════════════════════════════════════
elif secao == "🌡️ Variável Discreta — Temperatura":
    st.header("🌡️ Variável Discreta — Temperature (K)")
    st.markdown(
        "A temperatura superficial das estrelas é armazenada em Kelvin como valores inteiros. "
        "Para análise de distribuição, os dados foram categorizados em **6 faixas espectrais** "
        "inspiradas na sequência de Harvard (OBAFGKM)."
    )

    temp = df["Temperature (K)"]

    # Tabela de frequências por faixa
    st.subheader("1. Tabela de Frequências por Faixa Espectral")
    freq_abs  = df["Temp Categoria"].value_counts().reindex(TEMP_LABELS)
    total     = len(df)
    freq_rel  = (freq_abs / total * 100).round(2)
    freq_acum = freq_abs.cumsum()
    frel_acum = freq_rel.cumsum().round(2)
    tabela_temp = pd.DataFrame({
        "Faixa de Temperatura":      TEMP_LABELS,
        "Freq. Absoluta":            freq_abs.values.tolist(),
        "Freq. Relativa (%)":        freq_rel.values.tolist(),
        "Freq. Abs. Acumulada":      freq_acum.values.tolist(),
        "Freq. Rel. Acumulada (%)":  frel_acum.values.tolist(),
    })
    st.dataframe(tabela_temp, use_container_width=True, hide_index=True)

    # Histograma + Polígono de frequências
    st.subheader("2. Histograma e Polígono de Frequências")
    n_bins = st.slider("Número de classes (histograma)", 10, 50, 30, key="temp_bins")

    col1, col2 = st.columns(2)
    with col1:
        fig_hist = px.histogram(
            df, x="Temperature (K)", nbins=n_bins,
            title="Histograma — Temperature (K)",
            labels={"Temperature (K)": "Temperatura (K)", "count": "Frequência"},
            color_discrete_sequence=["steelblue"],
        )
        fig_hist.update_layout(bargap=0.05, height=380)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Polígono de frequências
        counts, borders = np.histogram(temp, bins=n_bins)
        midpoints = (borders[:-1] + borders[1:]) / 2
        x_poly = np.concatenate([[borders[0]], midpoints, [borders[-1]]])
        y_poly = np.concatenate([[0], counts, [0]])
        fig_poly = go.Figure()
        fig_poly.add_trace(go.Scatter(
            x=x_poly, y=y_poly, mode="lines+markers",
            line=dict(color="darkorange", width=2),
            marker=dict(size=5),
            fill="tozeroy", fillcolor="rgba(255,140,0,0.15)",
            name="Polígono",
        ))
        fig_poly.update_layout(
            title="Polígono de Frequências — Temperature (K)",
            xaxis_title="Temperatura (K)", yaxis_title="Frequência",
            height=380,
        )
        st.plotly_chart(fig_poly, use_container_width=True)

    # Boxplot
    st.subheader("3. Boxplot")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        fig_box = px.box(
            df, y="Temperature (K)",
            title="Boxplot Geral — Temperature (K)",
            color_discrete_sequence=["steelblue"],
            points="outliers",
        )
        fig_box.update_layout(height=420)
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b2:
        fig_box2 = px.box(
            df, x="Star type label", y="Temperature (K)",
            color="Star type label",
            color_discrete_sequence=PALETTE_6,
            title="Boxplot por Tipo Estelar — Temperature (K)",
            labels={"Star type label": "Tipo Estelar", "Temperature (K)": "Temperatura (K)"},
            category_orders={"Star type label": list(STAR_TYPE_NAMES.values())},
            points="outliers",
        )
        fig_box2.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig_box2, use_container_width=True)

    # Medidas descritivas
    st.subheader("4. Medidas Descritivas")
    medidas = medidas_descritivas(temp)
    render_medidas(medidas)

    with st.expander("Interpretação das medidas"):
        st.markdown(
            "- **Média (10.497 K) > Mediana (5.776 K)**: assimetria positiva — cauda à direita puxada pelas estrelas muito quentes.\n"
            "- **CV = 91%**: alta variabilidade relativa, reflexo da amplitude de 38.061 K.\n"
            "- **Assimetria de Pearson = 1,48**: confirmação de distribuição assimétrica à direita.\n"
            "- **Curtose = 0,83**: leve leptocurtose (mais concentração no centro que a normal).\n"
            "- **Distribuição bimodal**: dois grupos principais — estrelas frias (<3.500 K, 31,25%) e quentes (7.500–30.000 K, 40%)."
        )


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — VARIÁVEIS CONTÍNUAS
# ══════════════════════════════════════════════════════════════════════════════
elif secao == "📊 Variáveis Contínuas":
    st.header("📊 Variáveis Contínuas")
    st.markdown(
        "Três variáveis contínuas foram analisadas: **Luminosidade**, **Raio** e **Magnitude Absoluta**. "
        "Para Luminosidade e Raio, a forte assimetria justifica análise adicional na escala **log₁₀**."
    )

    var_opcoes = {
        "Luminosity(L/Lo)":          ("Luminosity (L/Lo)",      "Luminosidade (L/Lo)"),
        "log_Luminosity":            ("log₁₀(Luminosity)",      "log₁₀(Luminosidade)"),
        "Radius(R/Ro)":              ("Radius (R/Ro)",          "Raio (R/Ro)"),
        "log_Radius":                ("log₁₀(Radius)",         "log₁₀(Raio)"),
        "Absolute magnitude(Mv)":    ("Absolute Magnitude (Mv)","Magnitude Absoluta (Mv)"),
    }

    col_sel, _ = st.columns([2, 3])
    with col_sel:
        var_key = st.selectbox(
            "Variável analisada",
            options=list(var_opcoes.keys()),
            format_func=lambda k: var_opcoes[k][0],
        )
    nome_var, xlabel = var_opcoes[var_key]
    serie = df[var_key].dropna()

    # Histograma com KDE
    st.subheader(f"1. Histograma com KDE — {nome_var}")
    n_bins_c = st.slider("Número de classes", 10, 60, 30, key="cont_bins")
    fig_h = px.histogram(
        df.dropna(subset=[var_key]), x=var_key, nbins=n_bins_c,
        histnorm="probability density",
        color_discrete_sequence=["steelblue"],
        title=f"Histograma com KDE — {nome_var}",
        labels={var_key: xlabel},
    )
    # Adiciona KDE via scipy
    x_kde = np.linspace(serie.min(), serie.max(), 400)
    kde   = scipy_stats.gaussian_kde(serie)
    fig_h.add_trace(go.Scatter(
        x=x_kde, y=kde(x_kde), mode="lines",
        line=dict(color="darkorange", width=2.5),
        name="KDE",
    ))
    fig_h.update_layout(bargap=0.02, height=420)
    st.plotly_chart(fig_h, use_container_width=True)

    # Boxplot por tipo estelar
    st.subheader(f"2. Boxplot por Tipo Estelar — {nome_var}")
    fig_b = px.box(
        df.dropna(subset=[var_key]),
        x="Star type label", y=var_key,
        color="Star type label",
        color_discrete_sequence=PALETTE_6,
        title=f"Boxplot por Tipo Estelar — {nome_var}",
        labels={"Star type label": "Tipo Estelar", var_key: xlabel},
        category_orders={"Star type label": list(STAR_TYPE_NAMES.values())},
        points="outliers",
    )
    fig_b.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig_b, use_container_width=True)

    # Tabela de frequências
    st.subheader(f"3. Tabela de Frequências — {nome_var}")
    n_cl = st.slider("Número de classes (tabela)", 4, 12, 6, key="cont_nclass")
    tab_cont = tabela_freq_continua(serie, n_classes=n_cl)
    st.dataframe(tab_cont, use_container_width=True, hide_index=True)

    # Medidas descritivas
    st.subheader(f"4. Medidas Descritivas — {nome_var}")
    medidas = medidas_descritivas(serie)
    render_medidas(medidas)

    with st.expander("Interpretações por variável"):
        st.markdown(
            "**Luminosity (escala original):** Assimetria fortíssima (1,79) — a maioria das estrelas tem "
            "luminosidade baixa, mas hipergigantes atingem 849.420 L/Lo.\n\n"
            "**log₁₀(Luminosity):** Assimetria reduz para 1,41 e CV permanece alto pois a média (~0,7) "
            "cruza o zero — o CV perde interpretabilidade aqui.\n\n"
            "**Radius (escala original):** CV de 218%, confirmando enorme variabilidade. "
            "Raios de 0,008 a 1.948,5 R/Ro.\n\n"
            "**Absolute Magnitude (Mv):** Escala invertida — valores negativos indicam estrelas mais "
            "brilhantes. Assimetria negativa (-1,12): cauda à esquerda (hipergigantes muito brilhantes)."
        )


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — DIAGRAMA DE HERTZSPRUNG-RUSSELL
# ══════════════════════════════════════════════════════════════════════════════
elif secao == "🌌 Diagrama de Hertzsprung-Russell":
    st.header("🌌 Diagrama de Hertzsprung-Russell")
    st.markdown(
        "O **Diagrama H-R** relaciona **temperatura superficial** (eixo X, escala log invertida) "
        "e **luminosidade** (eixo Y, log₁₀). O **tamanho** de cada ponto é proporcional ao raio "
        "da estrela e a **cor** indica o tipo estelar."
    )

    df_hr = df.dropna(subset=["log_Luminosity"]).copy()
    # Normaliza raio para tamanho de marcador
    r_min, r_max = df_hr["Radius(R/Ro)"].min(), df_hr["Radius(R/Ro)"].max()
    df_hr["marker_size"] = 6 + 28 * (df_hr["Radius(R/Ro)"] - r_min) / (r_max - r_min)

    # Filtro por tipo estelar
    tipos_hr = st.multiselect(
        "Tipos estelares visíveis",
        options=list(STAR_TYPE_NAMES.values()),
        default=list(STAR_TYPE_NAMES.values()),
        key="hr_tipos",
    )
    df_hr_f = df_hr[df_hr["Star type label"].isin(tipos_hr)]

    fig_hr = px.scatter(
        df_hr_f,
        x="Temperature (K)",
        y="log_Luminosity",
        color="Star type label",
        size="marker_size",
        size_max=30,
        color_discrete_sequence=PALETTE_6,
        hover_data={
            "Temperature (K)": True,
            "Luminosity(L/Lo)": ":.4g",
            "Radius(R/Ro)": ":.3g",
            "Spectral Class": True,
            "Star color std": True,
            "marker_size": False,
        },
        labels={
            "Temperature (K)":  "Temperatura (K) — escala log",
            "log_Luminosity":   "log₁₀(Luminosidade)",
            "Star type label":  "Tipo Estelar",
            "Star color std":   "Cor",
        },
        title="Diagrama de Hertzsprung-Russell",
        category_orders={"Star type label": list(STAR_TYPE_NAMES.values())},
        opacity=0.85,
    )
    fig_hr.update_xaxes(type="log", autorange="reversed")
    fig_hr.update_layout(height=600, legend_title_text="Tipo Estelar")
    st.plotly_chart(fig_hr, use_container_width=True)

    with st.expander("Interpretação do Diagrama H-R"):
        st.markdown(
            "- **Sequência principal** (Seq. Principal / Anã Vermelha): faixa diagonal central — "
            "fusão de hidrogênio em equilíbrio.\n"
            "- **Anãs brancas**: canto inferior esquerdo — quentes, mas pouco luminosas (raio pequeno).\n"
            "- **Gigantes e supergigantes**: região superior — alta luminosidade, temperaturas variadas.\n"
            "- **Hipergigantes**: pontos maiores no topo — raios e luminosidades extremos.\n"
            "- **Anãs Marrons**: canto inferior direito — frias e pouco luminosas.\n"
            "- O eixo X está **invertido** (temperatura decrescente da esquerda para a direita), "
            "conforme convenção astronômica."
        )


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 — CORRELAÇÃO E REGRESSÃO
# ══════════════════════════════════════════════════════════════════════════════
elif secao == "📈 Correlação e Regressão":
    st.header("📈 Correlação de Pearson e Regressão Linear")

    NUM_COLS = [
        "Temperature (K)", "Luminosity(L/Lo)", "Radius(R/Ro)",
        "Absolute magnitude(Mv)", "log_Luminosity", "log_Radius",
    ]
    LABELS_LEGIVEL = {
        "Temperature (K)":          "Temperatura (K)",
        "Luminosity(L/Lo)":         "Luminosidade",
        "Radius(R/Ro)":             "Raio",
        "Absolute magnitude(Mv)":   "Magnitude Abs.",
        "log_Luminosity":           "log₁₀(Luminosidade)",
        "log_Radius":               "log₁₀(Raio)",
    }
    df_num = df[NUM_COLS].dropna()
    corr   = df_num.corr(method="pearson")

    # Heatmap
    st.subheader("1. Matriz de Correlação de Pearson")
    labels = [LABELS_LEGIVEL[c] for c in NUM_COLS]
    fig_heat = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        colorscale="RdBu", zmid=0,
        zmin=-1, zmax=1,
        text=corr.round(3).values.tolist(),
        texttemplate="%{text}",
        textfont={"size": 11},
        hoverongaps=False,
    ))
    fig_heat.update_layout(
        title="Correlação de Pearson — Star Dataset",
        height=500, width=650,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Identificação automática do par de maior correlação
    corr_abs = corr.abs().copy()
    vals = corr_abs.values.copy()
    np.fill_diagonal(vals, 0)
    # Zera triângulo superior
    vals_lt = np.tril(vals, k=-1)
    flat_idx = np.unravel_index(np.argmax(vals_lt), vals_lt.shape)
    var_x = NUM_COLS[flat_idx[0]]
    var_y = NUM_COLS[flat_idx[1]]
    r_max = corr.loc[var_x, var_y]

    st.info(
        f"**Par com maior correlação absoluta:** "
        f"`{LABELS_LEGIVEL[var_x]}` × `{LABELS_LEGIVEL[var_y]}`   |   "
        f"**r = {r_max:.4f}**"
    )

    # Seletor de par para regressão
    st.subheader("2. Regressão Linear Simples")
    col_x, col_y = st.columns(2)
    with col_x:
        sel_x = st.selectbox(
            "Variável X (preditora)",
            options=NUM_COLS,
            index=NUM_COLS.index(var_x),
            format_func=lambda k: LABELS_LEGIVEL[k],
            key="reg_x",
        )
    with col_y:
        sel_y = st.selectbox(
            "Variável Y (resposta)",
            options=NUM_COLS,
            index=NUM_COLS.index(var_y),
            format_func=lambda k: LABELS_LEGIVEL[k],
            key="reg_y",
        )

    dados = df_num[[sel_x, sel_y]].dropna()
    x_vals = dados[sel_x].values
    y_vals = dados[sel_y].values
    slope, intercept, r_value, p_value, se_slope = scipy_stats.linregress(x_vals, y_vals)
    y_pred   = slope * x_vals + intercept
    residuos = y_vals - y_pred
    r2       = r_value ** 2
    rmse     = np.sqrt(np.mean(residuos ** 2))

    # Métricas
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Correlação r",     f"{r_value:.4f}")
    mc2.metric("R² (determinação)", f"{r2:.4f}")
    mc3.metric("RMSE",             f"{rmse:.4f}")
    mc4.metric("p-valor",          f"{p_value:.2e}")

    sign = "+" if intercept >= 0 else "−"
    st.markdown(
        f"**Equação ajustada:**  "
        f"`ŷ = {slope:.4f} · x  {sign}  {abs(intercept):.4f}`"
    )

    col_d, col_r = st.columns(2)

    # Gráfico de dispersão com reta
    with col_d:
        x_line = np.linspace(x_vals.min(), x_vals.max(), 300)
        y_line = slope * x_line + intercept
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode="markers",
            marker=dict(color="steelblue", size=6, opacity=0.55,
                        line=dict(color="black", width=0.3)),
            name="Observações",
        ))
        fig_reg.add_trace(go.Scatter(
            x=x_line, y=y_line, mode="lines",
            line=dict(color="red", width=2),
            name="Reta ajustada",
        ))
        fig_reg.update_layout(
            title=f"Regressão: {LABELS_LEGIVEL[sel_x]} × {LABELS_LEGIVEL[sel_y]}",
            xaxis_title=LABELS_LEGIVEL[sel_x],
            yaxis_title=LABELS_LEGIVEL[sel_y],
            height=420,
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    # Gráfico de resíduos
    with col_r:
        fig_res = go.Figure()
        fig_res.add_trace(go.Scatter(
            x=y_pred, y=residuos, mode="markers",
            marker=dict(color="darkorange", size=6, opacity=0.6,
                        line=dict(color="black", width=0.3)),
            name="Resíduos",
        ))
        fig_res.add_hline(y=0, line_dash="dash", line_color="red", line_width=1.5)
        fig_res.update_layout(
            title="Resíduos vs. Valores Ajustados (ŷ)",
            xaxis_title="Valores Ajustados (ŷ)",
            yaxis_title="Resíduos (y − ŷ)",
            height=420,
        )
        st.plotly_chart(fig_res, use_container_width=True)

    with st.expander("Interpretação da Regressão Padrão (log₁₀(L) × Magnitude Abs.)"):
        st.markdown(
            f"- **r = −0,9766**: correlação muito forte e negativa — quanto maior a luminosidade, "
            f"menor (mais negativa) a magnitude absoluta, conforme esperado pela física estelar.\n"
            f"- **R² = 95,37%**: a log-luminosidade explica ~95% da variância da magnitude absoluta. "
            f"Excelente poder preditivo.\n"
            f"- **RMSE = 2,26 mag**: erro médio de ~2,3 magnitudes no modelo linear.\n"
            f"- **p-valor ≈ 8 × 10⁻¹⁶¹**: coeficiente angular estatisticamente significativo "
            f"(muito abaixo de α = 0,05).\n"
            f"- **Resíduos:** o gráfico de resíduos mostra padrão em leque (heterocedasticidade leve), "
            f"indicando que a relação não é perfeitamente linear em toda a faixa."
        )
