# Validação de Modelos de Clusterização (GTD)

Projeto para geração e visualização de clusters geográficos do Global Terrorism Database (GTD). O pipeline consiste em um script Python que lê um CSV, aplica HDBSCAN (ou DBSCAN com métrica de Haversine como fallback) e produz `clusters_data.json`. Esse JSON é consumido por uma página estática (`index.html`) que exibe um mapa interativo com camadas de clusters e heatmap, além de filtros por ano e região.

## Descrição
- `generate_clusters_json.py`:
  - Detecta automaticamente colunas de latitude/longitude (`latitude`/`lat`, `longitude`/`lon`).
  - Mantém campos adicionais se presentes: `nkill` (vítimas fatais), `iyear` (ano), `region_txt` ou `region`.
  - Converte coordenadas para radianos e tenta clusterizar com HDBSCAN; se indisponível, utiliza DBSCAN com métrica de Haversine.
  - Gera um `clusters_data.json` contendo cada ponto com chaves: `lat`, `lon`, `cluster_id` e, quando disponíveis, `nkill`, `iyear`, `region_txt`.
- `index.html`:
  - Usa Leaflet e MarkerCluster para visualizar pontos e agrupamentos no mapa.
  - Oferece uma camada de heatmap (Leaflet.heat) e uma camada de clusters alternáveis.
  - Permite filtros por `Ano` e `Região`, e resumo de contagem de pontos/ruído.
  - Carrega automaticamente `clusters_data.json` (com fallback para upload manual).

## Como Rodar Localmente

### 1) Preparar ambiente e instalar dependências
- Pré-requisitos: Python 3.11+ e `pip`.
- Instale as dependências:
  - `pip install -r requirements.txt`
  - Opcional (para executar notebooks): `pip install jupyter` (não é importado diretamente, mas útil para abrir `.ipynb`).
  - Baixe o arquivo `globalterrorismdb_0718dist.csv` do [Kaggle](https://www.kaggle.com/datasets/START-UMD/gtd) e coloque na pasta do projeto.

### 2) Gerar o arquivo `clusters_data.json`
- Estrutura básica de uso (com valores padrão):
  - `python generate_clusters_json.py --input globalterrorismdb_0718dist.csv --output clusters_data.json --eps 0.005 --min-samples 10 --max-points 80000`
- Argumentos disponíveis:
  - `--input`: caminho para o CSV (por padrão `globalterrorismdb_0718dist.csv`).
  - `--output`: nome do JSON gerado (por padrão `clusters_data.json`).
  - `--eps`: raio (em radianos) para DBSCAN quando usado como fallback.
  - `--min-samples`: número mínimo de amostras para formar um cluster.
  - `--max-points`: amostra máxima (aleatória) de pontos a processar, para limitar volume.
- Observações:
  - O script procura automaticamente as colunas de latitude/longitude e filtra coordenadas inválidas.
  - Se HDBSCAN estiver disponível, será usado; caso contrário, DBSCAN (métrica `haversine`).

### 3) Abrir o `index.html` e visualizar
- Coloque o `clusters_data.json` no mesmo diretório que o `index.html`.
- Opção A (simples): abra `index.html` diretamente no navegador. Se o carregamento automático do JSON falhar, use o seletor de arquivo "Carregar JSON" na lateral.
- Opção B (servidor local): sirva a pasta via HTTP (recomendado para evitar políticas de `file://`). Exemplo:
  - `python -m http.server 8000`
  - Abra `http://localhost:8000/index.html` no navegador.
- Interações:
  - Alternar entre "Clusters" e "Heatmap".
  - Filtrar por ano e região; limpar filtros.
  - Ajustar raio e borrado do heatmap.

### Vídeo (passo a passo)
- Assista ao vídeo explicando como rodar o `index.html` localmente e usar os filtros:
  - [Execução local e uso da interface]([tutorial_rodar_index.mp4](https://youtu.be/SGfJHvt0iA0))

## Deploy (Vercel)
- O projeto está hospedado na Vercel: `https://validacaomodelo-clust.vercel.app/`
- Configuração relevante em `vercel.json`:
  - `cleanUrls: true`, `trailingSlash: false`.
  - Cabeçalho de cache para `clusters_data.json` (`Cache-Control: public, max-age=300`).
- Fluxo esperado: após gerar/atualizar `clusters_data.json`, a página `index.html` o consumirá e exibirá os clusters.

## Estrutura de Arquivos
- `Notebooks/`: análises exploratórias e de clusterização (p.ex. uso de `pandas`, `numpy`, `matplotlib`, `seaborn`, módulos de `sklearn` e `scipy.sparse`).
- `generate_clusters_json.py`: pipeline de leitura do CSV, preparação dos dados e clusterização (HDBSCAN/DBSCAN), produzindo o JSON.
- `clusters_data.json`: saída consumida pelo front-end; lista de pontos com `lat`, `lon`, `cluster_id` e atributos opcionais.
- `index.html`: front-end estático em Leaflet para visualização interativa dos resultados com clusters e heatmap, incluindo filtros.
- `vercel.json`: configuração de deploy e headers para o JSON.
- `requirements.txt`: dependências Python diretas usadas no script e nos notebooks.

