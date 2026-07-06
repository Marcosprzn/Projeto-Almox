# Projeto Almox

Automação para capturar **valores unitários** de itens no **MEGA ERP** (sistema
desktop/on-premise) e gerar uma planilha Excel, a partir de uma lista de códigos
lida de um PDF.

## Situação atual

O acesso ao banco Oracle e à API REST do Mega **não foi liberado** pelo TI, então
a captura é feita por **RPA** (automação de tela) sobre a janela do Mega.

- Fonte dos códigos: um PDF de relatório ("Saída/Falta Valor Unitário").
- Captura do preço: filtra o código no Mega e lê a grade de resultados.
- Saída: `resultados_almox.xlsx`.

> O PDF com dados reais **não** está no repositório (é entrada sensível).
> Copie o seu PDF para a pasta ao testar.

## Arquivos

| Arquivo | Função |
|---|---|
| `almox_bot.py` | Bot principal: PDF → filtra no Mega → lê a grade → Excel |
| `inspecionar_mega.py` | Descobre os controles reais da janela do Mega (para trocar cliques por pixel por controles) |
| `diagnostico_grade.py` | Testa leitura da grade em várias posições (UIA) |
| `explorar_grade.py` | Explora a árvore de controles da grade (UIA) |
| `teste_win32.py` | Testa backend win32 e screenshot da grade |
| `mega_api.py` | Cliente REST do Mega (caso a API seja liberada no futuro) |
| `instalar_dependencias.bat` | Instala pywinauto, openpyxl e pypdf |
| `executar_almox.bat` | Executa o bot |

## Instalação

```bat
pip install pywinauto openpyxl pypdf
```

> `pypdf` é o sucessor do `PyPDF2` (mesma API). O código aceita os dois,
> mas prefira `pypdf` — instala limpo no Python 3.11+.

ou rode `instalar_dependencias.bat`.

## Uso

1. Abra o Mega na tela de consulta com o campo de código e a grade visíveis.
2. Rode `executar_almox.bat` (ou `python almox_bot.py`).
3. Selecione o PDF com os códigos.
4. Durante a execução: **F8** pausa/retoma, **ESC** aborta (salvando o que já foi lido).

## Próximo passo

Trocar os cliques por **coordenadas de pixel** por **controles reais** da janela
(via `pywinauto`), usando a saída de `inspecionar_mega.py`. Isso torna o bot
imune a mudanças de posição/resolução da janela.
