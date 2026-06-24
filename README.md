# Análise Estatística Descritiva do Star Dataset

**Grupo:** Antonio Henrique Q. V. Lopes, Jamily V. Gonçalves e Júlia P. Souza  
**Disciplina:** Probabilidade e Estatística A — UFG  
**Dataset:** Star Dataset to Predict Star Types (Kaggle) — 240 observações, 6 tipos estelares  
**Arquivo de dados:** `6 class csv.csv`

---

## Dashboard Interativo

> **Principal forma de visualizar o projeto.**

O dashboard reúne todas as análises em uma interface interativa no navegador,
com gráficos dinâmicos, tabelas e filtros por tipo estelar.

### Como rodar

```bash
python -m streamlit run dashboard.py
```

Acesse em: **http://localhost:8501**

> Se o navegador não abrir automaticamente, cole o endereço acima manualmente.

### O que o dashboard inclui

- Visão geral do dataset com filtros por tipo estelar
- Análise das variáveis qualitativas: Star color, Spectral Class, Star type, is_Giant
- Análise da variável discreta: Temperature (K) com histograma, polígono e boxplot
- Análise das variáveis contínuas: Luminosity, Radius, Magnitude Absoluta (escalas original e log₁₀)
- Análise das variáveis derivadas: log₁₀(Temperature) e Luminosity/Radius²
- Diagrama de Hertzsprung-Russell interativo
- Correlação e regressão linear simples

---

## Instalação das Dependências

```bash
pip install -r requirements.txt
```

Bibliotecas: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `plotly`, `streamlit`.

---

## Scripts de Análise (opcional)

Os scripts abaixo geram os gráficos estáticos em PNG e os CSVs de separatrizes,
salvos na pasta `graficos/`. Rode-os apenas se quiser regenerar os arquivos de saída.
**Para visualizar o projeto, use o dashboard acima — não é necessário rodar os scripts.**

Execute na ordem a partir da pasta raiz:

```bash
python scripts/analise_qualitativas.py
python scripts/analise_discreta.py
python scripts/analise_continuas.py
python scripts/diagrama_hr.py
python scripts/regressao_linear.py
```

---

## Estrutura de Pastas

```
trabalho final PE/
├── 6 class csv.csv               ← dataset original
├── dashboard.py                  ← dashboard interativo (Streamlit + Plotly)
├── requirements.txt
├── README.md
├── scripts/
│   ├── analise_qualitativas.py   ← Star color, Spectral Class, Star type, is_Giant
│   ├── analise_discreta.py       ← Temperature (K)
│   ├── analise_continuas.py      ← Luminosity, Radius, Magnitude, + variáveis derivadas
│   ├── diagrama_hr.py            ← Diagrama de Hertzsprung-Russell
│   ├── regressao_linear.py       ← Correlação e regressão linear
│   └── gerar_relatorio.py        ← Gerador do documento Word (ABNT)
└── graficos/                     ← criada automaticamente pelos scripts
    ├── qualitativas/
    ├── discreta/
    ├── continuas/
    ├── regressao/
    └── diagrama_hr.png
```

---

## Variáveis do Dataset

### Originais (7)

| Coluna                 | Tipo                  | Descrição                        |
|------------------------|-----------------------|----------------------------------|
| Temperature (K)        | Quantitativa discreta | Temperatura superficial (Kelvin) |
| Luminosity(L/Lo)       | Quantitativa contínua | Luminosidade relativa ao Sol     |
| Radius(R/Ro)           | Quantitativa contínua | Raio relativo ao Sol             |
| Absolute magnitude(Mv) | Quantitativa contínua | Brilho intrínseco (escala Mv)    |
| Star color             | Qualitativa nominal   | Cor observada da estrela         |
| Spectral Class         | Qualitativa ordinal   | Classe espectral (O B A F G K M) |
| Star type              | Qualitativa ordinal   | 0=Anã Marrom … 5=Hipergigante    |

### Derivadas (3)

| Coluna                  | Fórmula                                  | Descrição                                     |
|-------------------------|------------------------------------------|-----------------------------------------------|
| log10_Temperature       | log₁₀(Temperature (K))                  | Temperatura em escala logarítmica             |
| Luminosity_per_Radius2  | Luminosity(L/Lo) / Radius(R/Ro)²        | Proxy de temperatura via Stefan-Boltzmann     |
| is_Giant                | 'Gigante' se Star type ≥ 3, senão 'Não Gigante' | Classificação binária: gigantes vs anãs |
