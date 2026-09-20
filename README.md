# pylibre

Interface de linha de comando para converter arquivos **EPUB** em **texto puro** (`.txt`).

O projeto usa apenas a **biblioteca padrão do Python** — não há dependências externas para instalar.

## Funcionalidades

- Converte um ou vários EPUBs em texto puro, seguindo a ordem dos capítulos (`<spine>`);
- Preserva a estrutura de leitura: parágrafos, títulos, listas e outras quebras de bloco;
- Remove o ruído visual: tags HTML, `<head>`, `<script>` e `<style>`;
- Converte entidades HTML (`&nbsp;`, `&mdash;`, …) para caracteres legíveis;
- Mantém o texto alternativo de imagens (`alt`), quando existir;
- Inclui (opcionalmente) título e autor extraídos dos metadados do livro.

## Requisitos

- Python **3.9 ou superior** (testado com Python 3.14)

## Instalação

A instalação é opcional — o projeto também pode ser usado sem instalar (ver [Uso](#rodando-sem-instalar)).

```bash
git clone <url-do-repositorio>
cd pylibre
pip install -e .        # instalação em modo editável
# ou
pip install .           # instalação comum
```

A instalação registra o comando `pylibre` no `PATH`.

## Uso

```bash
pylibre livro.epub                  # gera livro.txt ao lado do EPUB
pylibre livro.epub -o saida.txt     # escolhe o nome do arquivo de saída
pylibre --no-meta livro.epub        # sem o cabeçalho de título/autor
pylibre a.epub b.epub               # converte vários EPUBs de uma vez
```

### Opções

| Opção | Descrição |
| --- | --- |
| `epub` | Um ou mais arquivos `.epub` de entrada. |
| `-o, --output ARQ` | Arquivo de saída. Válido apenas com **um único** EPUB de entrada. |
| `--no-meta` | Não inclui título e autor no início do `.txt`. |
| `-h, --help` | Mostra a mensagem de ajuda e sai. |

Sem `-o`, o arquivo de saída é `<entrada>.txt` na mesma pasta do EPUB
(ex.: `livro.epub` → `livro.txt`).

### Exemplo de saída

```
O problema dos três corpos
Cixin Liu

LISTA DE PERSONAGENS

Os nomes chineses são escritos com o sobrenome na frente.

A família Ye

Ye Zhetai

Físico, professor na Universidade Tsinghua
...
```

### Códigos de saída

| Código | Significado |
| --- | --- |
| `0` | Todos os arquivos foram convertidos com sucesso. |
| `1` | Pelo menos um arquivo falhou (os demais continuam sendo processados). |
| `2` | Erro de uso da linha de comando (ex.: `-o` com mais de um EPUB). |

## Rodando sem instalar

```bash
python3 -m pylibre livro.epub
```

## Estrutura do projeto

```
pylibre/
├── pyproject.toml        # definição do pacote e do comando `pylibre`
├── README.md
└── pylibre/
    ├── __init__.py       # nome e versão do pacote
    ├── __main__.py       # suporte a `python3 -m pylibre`
    ├── cli.py            # interface de linha de comando (argparse)
    └── epub.py           # extração de texto do EPUB (biblioteca padrão)
```

## Como funciona

1. **Descoberta** — lê `META-INF/container.xml` para localizar o arquivo OPF raiz;
2. **Metadados** — extrai título (`dc:title`) e autores (`dc:creator`);
3. **Ordem** — segue o `<spine>` para processar os capítulos na ordem correta;
4. **Extração** — percorre cada documento XHTML mantendo as quebras de bloco
   (`p`, `h1`–`h6`, `li`, `blockquote`, …) e descartando `<head>`, `<script>`
   e `<style>`;
5. **Limpeza** — normaliza espaços e quebras de linha, converte entidades HTML
   e junta tudo em um único `.txt` UTF-8.

## Limitações conhecidas

- Blocos `pre` (texto pré-formatado) perdem os espaços internos na normalização;
- EPUBs protegidos por DRM não são suportados;
- As células de tabelas são extraídas na ordem do documento (uma por linha).
