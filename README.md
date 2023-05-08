# Introdução

O repositório em questão possui métodos responsáveis por analisar um GFC e computar o grafo reduzido e um conjunto de arcos essenciais.

Estes algoritmos são baseados na definição de Chusho.

# Arquivos

Os arquivos `util.py` e `app.py` são os dois principais para executar a dashboard que exibe o grafo.

No arquivo `util.py` temos todos os métodos responsáveis por aplicar as regras definidas no artigo base.

Já o arquivo `app.py` possui o código que utiliza das bibliotecas `Plotly` e `Dash` para plotagem do grafo. 

# Execução

Para executar o projeto inicialmente é necessário ter as dependências abaixo instaladas:

```requirements.txt
dash
plotly
networkx
numpy
pydot
dash_core_components
dash_html_components
```
Elas podem ser instaladas de uma só vez, basta colocar o conteúdo acima em um arquivo requirements.txt e executar o comando `pip3 install -r requirements.txt`.

Após instalar as dependências, para iniciar o aplicativo basta executar `python3 app.py` isso abrirá a dashboard em `http://127.0.0.1:8050/`.

Na dashboard possuímos basicamente duas caixas de seleção, a primeira exibe todos os arquivos .dot dentro da pasta `./dots/`. Ao selecionar um arquivo, ele será exibido na tela.

Já a segunda caixa de seleção possui alguns métodos que podem ser aplicados, como Aplicar Regra 1, Aplicar Regra 2, Aplicar Regra 3 e 4 e Aplicar todas as Regras.

Ao selecionar uma opção na caixa de seleção à direita, o grafo atualizado será exibido no lado direito da tela. O grafo inicial continua sendo exibido no lado esquerdo da tela.
