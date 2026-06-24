# Análise estatística descritiva do Star Dataset

**Grupo**: Antonio Henrique Q. V. Lopes, Jamily V. Gonçalves e Júlia P. Souza   

---

**Disciplina:** Probabilidade e Estatística A — UFG  
**Dataset:** Star Dataset to Predict Star Types (Kaggle)  
**Arquivo de dados:** `6 class csv.csv`

---

## Objetivo

Realizar análise estatística descritiva completa do Star Dataset, abrangendo:
variáveis qualitativas, variável discreta (temperatura), variáveis contínuas
(luminosidade, raio, magnitude), Diagrama de Hertzsprung-Russell e regressão linear simples.

---

## Estrutura de Pastas

```
trabalho final PE/
├── 6 class csv.csv          ← dataset original
├── requirements.txt         ← dependências Python
├── README.md
├── scripts/
│   ├── analise_qualitativas.py
│   ├── analise_discreta.py
│   ├── analise_continuas.py
│   ├── diagrama_hr.py
│   └── regressao_linear.py
└── graficos/                ← criada automaticamente ao rodar os scripts
    ├── qualitativas/
    ├── discreta/
    ├── continuas/
    ├── regressao/
    └── diagrama_hr.png
```

---

## Instalação das Dependências

```bash
pip install -r requirements.txt
```

Bibliotecas utilizadas: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`.

---

## Como Executar

Execute os scripts **na ordem abaixo**, a partir da pasta raiz do projeto:

### 1. Variáveis Qualitativas

```bash
python scripts/analise_qualitativas.py
```

Gera tabelas de frequência e gráficos para **Star color**, **Spectral Class** e **Star type**.  
Saída: `graficos/qualitativas/`

### 2. Variável Discreta — Temperature (K)

```bash
python scripts/analise_discreta.py
```

Categoriza a temperatura em 6 faixas espectrais, gera tabela completa, histograma,
polígono de frequências, medidas descritivas e boxplots.  
Saída: `graficos/discreta/`

### 3. Variáveis Contínuas

```bash
python scripts/analise_continuas.py
```

Analisa Luminosidade, Raio e Magnitude Absoluta (escalas original e log₁₀).
Tabelas com densidade, histogramas com KDE, boxplots por tipo estelar e medidas descritivas.  
Saída: `graficos/continuas/`

### 4. Diagrama de Hertzsprung-Russell

```bash
python scripts/diagrama_hr.py
```

Constrói o diagrama HR clássico: temperatura (log, invertida) × log(luminosidade),
com pontos coloridos por tipo estelar e tamanho proporcional ao raio.  
Saída: `graficos/diagrama_hr.png`

### 5. Correlação e Regressão Linear

```bash
python scripts/regressao_linear.py
```

Calcula a matriz de correlação de Pearson, identifica automaticamente o par mais
correlacionado, ajusta regressão linear simples e gera gráficos de dispersão e resíduos.  
Saída: `graficos/regressao/`

---

## Descrição das Variáveis

| Coluna                  | Tipo                    | Descrição                         |
|-------------------------|-------------------------|-----------------------------------|
| Temperature (K)         | Quantitativa discreta   | Temperatura efetiva da estrela    |
| Luminosity(L/Lo)        | Quantitativa contínua   | Luminosidade relativa ao Sol      |
| Radius(R/Ro)            | Quantitativa contínua   | Raio relativo ao Sol              |
| Absolute magnitude(Mv)  | Quantitativa contínua   | Brilho intrínseco da estrela      |
| Star type               | Qualitativa ordinal     | 0=Anã Marrom … 5=Hipergigante     |
| Star color              | Qualitativa nominal     | Cor observada da estrela          |
| Spectral Class          | Qualitativa ordinal     | Classe espectral (O B A F G K M)  |
