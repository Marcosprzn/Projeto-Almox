import time
import os
import sys
import re
import unicodedata
import ctypes
import atexit
import traceback
import tkinter as tk
from tkinter import filedialog
# ============================================================
# ENTRADA (mouse + teclado) via API nativa do Windows (ctypes)
# Substitui o pywinauto para NAO depender de pywin32/comtypes/win32ui,
# que causam "DLL load failed" / "modulo nao encontrado" em varios PCs.
# Usa apenas o proprio Windows (ja incluso no Python).
# ============================================================
_WORD = ctypes.c_ushort
_DWORD = ctypes.c_ulong
_LONG = ctypes.c_long
_ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)
_u32 = ctypes.windll.user32


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", _WORD), ("wScan", _WORD),
                ("dwFlags", _DWORD), ("time", _DWORD),
                ("dwExtraInfo", _ULONG_PTR)]


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", _LONG), ("dy", _LONG),
                ("mouseData", _DWORD), ("dwFlags", _DWORD),
                ("time", _DWORD), ("dwExtraInfo", _ULONG_PTR)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", _KEYBDINPUT), ("mi", _MOUSEINPUT)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", _DWORD), ("u", _INPUTUNION)]


_INPUT_KEYBOARD = 1
_KEYEVENTF_KEYUP = 0x0002
_KEYEVENTF_UNICODE = 0x0004

# Virtual-Key codes usados pelo bot
VK_CONTROL = 0x11
VK_DELETE = 0x2E
VK_DOWN = 0x28
VK_HOME = 0x24
VK_A = 0x41
VK_C = 0x43


def _enviar(*inputs):
    n = len(inputs)
    arr = (_INPUT * n)(*inputs)
    _u32.SendInput(n, arr, ctypes.sizeof(_INPUT))


def _in_vk(vk, up=False):
    ki = _KEYBDINPUT(vk, 0, _KEYEVENTF_KEYUP if up else 0, 0, None)
    return _INPUT(_INPUT_KEYBOARD, _INPUTUNION(ki=ki))


def _in_uni(ch, up=False):
    fl = _KEYEVENTF_UNICODE | (_KEYEVENTF_KEYUP if up else 0)
    ki = _KEYBDINPUT(0, ord(ch), fl, 0, None)
    return _INPUT(_INPUT_KEYBOARD, _INPUTUNION(ki=ki))


def tecla(vk):
    """Pressiona e solta uma tecla (Virtual-Key code)."""
    _enviar(_in_vk(vk), _in_vk(vk, up=True))


def ctrl_mais(vk):
    """Ctrl + tecla (ex.: Ctrl+C, Ctrl+A, Ctrl+Home)."""
    _enviar(_in_vk(VK_CONTROL), _in_vk(vk),
            _in_vk(vk, up=True), _in_vk(VK_CONTROL, up=True))


def digitar(texto):
    """Digita um texto caractere a caractere (independe do layout do teclado)."""
    for ch in texto:
        _enviar(_in_uni(ch), _in_uni(ch, up=True))


def clicar(x, y):
    """Move o mouse e da um clique esquerdo em (x, y)."""
    _MOUSEEVENTF_LEFTDOWN = 0x0002
    _MOUSEEVENTF_LEFTUP = 0x0004
    _u32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    _u32.mouse_event(_MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.02)
    _u32.mouse_event(_MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
import openpyxl
# PyPDF2 foi descontinuado e renomeado para "pypdf" (mesma API).
# Usa pypdf se estiver instalado; senao, cai no PyPDF2.
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# ============================================================
# CAPTURA QUALQUER CRASH (mesmo fora do try/except)
# ============================================================
ARQUIVO_CRASH = os.path.join(os.path.dirname(__file__) or ".", "crash_almox.txt")

def salvar_crash(tipo, mensagem, tb=None):
    with open(ARQUIVO_CRASH, "a", encoding="utf-8") as f:
        f.write(f"\n=== {tipo} em {time.strftime('%H:%M:%S')} ===\n")
        f.write(f"{mensagem}\n")
        if tb:
            traceback.print_exc(file=f)

def handler_excecao(tipo, valor, tb):
    salvar_crash("EXCECAO NAO TRATADA", str(valor), tb)
    print(f"\n[CRASH] Erro salvo em: {ARQUIVO_CRASH}")
    print(f"[CRASH] {tipo.__name__}: {valor}")
    input("Pressione ENTER para fechar...")

sys.excepthook = handler_excecao

atexit.register(lambda: salvar_crash("ATEXIT", "Programa finalizado"))

with open(ARQUIVO_CRASH, "w", encoding="utf-8") as f:
    f.write(f"LOG DE CRASH - ALMOX BOT\n")
    f.write(f"Inicio: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write("=" * 50 + "\n")

# ============================================================
# CONFIGURACOES
# ============================================================
EDIT_COORDS       = (328, 280)
FILTRAR_COORDS    = (416, 678)
PRIMEIRA_LINHA    = (620, 267)  # Ponto DENTRO da grade (TcxGridSite).
                                # Nao precisa ser exatamente a 1a linha:
                                # o bot da Ctrl+Home para ir ao topo.

PASTA_ATUAL = os.path.dirname(__file__)
EXCEL_PATH  = os.path.join(PASTA_ATUAL, "resultados_almox.xlsx")

BOT_RODANDO = True
PAUSADO = False

# ============================================================
# PAUSA F8
# ============================================================
def verificar_pausa():
    global PAUSADO, BOT_RODANDO
    # ESC = abortar a automacao
    if ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000:
        BOT_RODANDO = False
        print("\n  [ESC] Abortando automacao...")
        return
    if ctypes.windll.user32.GetAsyncKeyState(0x77) & 0x8000:
        PAUSADO = not PAUSADO
        if PAUSADO:
            print("\n  [F8] PAUSADO. Pressione F8 para retomar...")
        else:
            print("\n  [F8] Retomando...")
        time.sleep(0.5)
    while PAUSADO:
        if ctypes.windll.user32.GetAsyncKeyState(0x77) & 0x8000:
            PAUSADO = False
            print("\n  [F8] Retomando...")
            time.sleep(0.5)
        time.sleep(0.1)

# ============================================================
# ROOT TK UNICO (reutilizado para dialogo e clipboard)
# ============================================================
# Criar/destruir varios Tk() no mesmo processo pode deixar o
# interpretador Tcl instavel. Mantemos um unico root oculto.
_TK_ROOT = None

def _get_root():
    global _TK_ROOT
    if _TK_ROOT is None:
        _TK_ROOT = tk.Tk()
        _TK_ROOT.withdraw()
    return _TK_ROOT

# ============================================================
# SELECIONAR PDF
# ============================================================
def selecionar_pdf():
    root = _get_root()
    root.attributes("-topmost", True)
    caminho = filedialog.askopenfilename(
        parent=root,
        title="Selecione o PDF com os codigos",
        filetypes=[("Arquivos PDF", "*.pdf"), ("Todos", "*.*")]
    )
    root.attributes("-topmost", False)
    return caminho

# ============================================================
# LER PDF
# ============================================================
def ler_pdf(caminho):
    linhas = []
    with open(caminho, "rb") as f:
        reader = PdfReader(f)
        for pagina in reader.pages:
            texto = pagina.extract_text() or ""
            for linha in texto.split("\n"):
                linha = linha.strip()
                if not linha:
                    continue
                dados = parse_linha(linha)
                if dados:
                    linhas.append(dados)
    return linhas

def parse_linha(linha):
    partes = re.split(r"(\d{2}/\d{2}/\d{4})", linha)
    if len(partes) < 3:
        return None
    antes_data = partes[0].strip()
    data = partes[1].strip()
    depois_data = partes[2].strip()
    m = re.match(r"^(\d{2}\.\d{3})", antes_data)
    if not m:
        return None
    codigo = m.group(1)
    resto = antes_data[m.end():].strip()
    dept_codigo = ""
    dept_nome = ""
    descricao = resto
    m_dept = re.search(r"(\d{3})([A-Za-z\u00C0-\u00FF].*)$", resto)
    if m_dept:
        descricao = resto[:m_dept.start()].strip()
        dept_codigo = m_dept.group(1)
        dept_nome = m_dept.group(2).strip()
    campos = depois_data.split()
    req = campos[0] if len(campos) > 0 else ""
    qtd = ""
    unidade = ""
    val_unit = ""
    val_total = ""
    if len(campos) > 1:
        m_qtd = re.match(r"([\d.,]+)([A-Za-z].*)$", campos[1])
        if m_qtd:
            qtd = m_qtd.group(1)
            unidade = m_qtd.group(2).strip()
        else:
            qtd = campos[1]
    if len(campos) > 2:
        val_unit = campos[2]
    if len(campos) > 3:
        val_total = campos[3]
    return {
        "codigo": codigo, "descricao": descricao,
        "dept_codigo": dept_codigo, "dept_nome": dept_nome,
        "data": data, "req": req, "qtd": qtd,
        "unidade": unidade, "val_unit": val_unit, "val_total": val_total,
    }

def codigos_unicos(linhas):
    vistos = set()
    unicos = []
    for item in linhas:
        c = item["codigo"]
        if c not in vistos:
            vistos.add(c)
            unicos.append(c)
    return unicos

# ============================================================
# LER CADA LINHA DA GRADE navegando com seta para baixo
# ============================================================
# Marcador usado para detectar quando o Ctrl+C nao copiou nada
# (evita ler o conteudo antigo/repetido do clipboard).
SENTINELA_VAZIA = "___ALMOX_CLIPBOARD_VAZIO___"

# ------------------------------------------------------------
# CLIPBOARD via API nativa do Windows (Win32).
# O tkinter falha ao ler texto colado por apps Delphi (MEGA):
# o MEGA copia como CF_UNICODETEXT e o tkinter pede outro formato,
# resultando em "cannot clipboard". A API Win32 le/escreve exatamente
# o formato certo e nao lanca esse erro.
# ------------------------------------------------------------
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

# argtypes/restypes corretos (essencial no Python 64 bits, senao os
# ponteiros/handles estouram e a leitura falha silenciosamente).
_user32.OpenClipboard.argtypes = [ctypes.c_void_p]
_user32.GetClipboardData.restype = ctypes.c_void_p
_user32.GetClipboardData.argtypes = [ctypes.c_uint]
_user32.SetClipboardData.restype = ctypes.c_void_p
_user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
_kernel32.GlobalLock.restype = ctypes.c_void_p
_kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
_kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
_kernel32.GlobalAlloc.restype = ctypes.c_void_p
_kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]

def _abrir_clipboard(tentativas=10):
    # O clipboard pode estar ocupado por outro processo; tenta algumas vezes.
    for _ in range(tentativas):
        if _user32.OpenClipboard(0):
            return True
        time.sleep(0.05)
    return False

def ler_clipboard():
    if not _abrir_clipboard():
        return ""
    try:
        handle = _user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        ptr = _kernel32.GlobalLock(handle)
        if not ptr:
            return ""
        try:
            return ctypes.c_wchar_p(ptr).value or ""
        finally:
            _kernel32.GlobalUnlock(handle)
    except Exception:
        return ""
    finally:
        _user32.CloseClipboard()

def set_clipboard(texto):
    if not _abrir_clipboard():
        return
    try:
        _user32.EmptyClipboard()
        buf = ctypes.create_unicode_buffer(texto)
        tamanho = ctypes.sizeof(buf)
        handle = _kernel32.GlobalAlloc(GMEM_MOVEABLE, tamanho)
        if not handle:
            return
        ptr = _kernel32.GlobalLock(handle)
        if ptr:
            ctypes.memmove(ptr, buf, tamanho)
            _kernel32.GlobalUnlock(handle)
            # Apos SetClipboardData o sistema passa a ser dono do handle.
            _user32.SetClipboardData(CF_UNICODETEXT, handle)
    except Exception:
        pass
    finally:
        _user32.CloseClipboard()

def sem_acento(s):
    """Remove acentos e deixa minusculo, para comparar textos (ex.: Saida)."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

# Palavras que so aparecem na linha de CABECALHO copiada pelo cxGrid.
_MARCADORES_CABECALHO = ("data do movimento", "vl.saida", "movimentacao")

def _eh_cabecalho(linha):
    baixo = sem_acento(linha)
    return any(m in baixo for m in _MARCADORES_CABECALHO)

# Guarda o conteudo bruto do 1o Ctrl+C, so para diagnostico.
_DEBUG_RAW_SALVO = False

def parse_linha_grid(texto):
    """Converte o texto copiado do cxGrid em dict.

    O Ctrl+C do cxGrid inclui a linha de CABECALHO junto com o(s)
    registro(s). Separamos por linha, descartamos o cabecalho e lemos
    a linha de dados (a ultima nao-cabecalho).
    """
    if not texto:
        return None
    linhas = [l for l in texto.replace("\r", "").split("\n") if l.strip()]
    if not linhas:
        return None
    # Mantem apenas as linhas de dados (fora cabecalho)
    dados = [l for l in linhas if not _eh_cabecalho(l)]
    if not dados:
        return None
    cols = dados[-1].split("\t")   # ultima linha = registro selecionado
    return {
        "tipo": cols[0].strip() if len(cols) > 0 else "",
        "data": cols[2].strip() if len(cols) > 2 else "",
        "vl_saida": cols[9].strip() if len(cols) > 9 else "",
    }

def navegar_grade():
    """Clica na primeira linha, navega pra baixo ate 'Final', retorna precos."""
    linhas_lidas = []
    ultimo_texto = None
    try:
        time.sleep(0.5)
        # Entra na grade (TcxGridSite) com um clique...
        clicar(*PRIMEIRA_LINHA)
        time.sleep(0.3)
        # ...e sobe para o PRIMEIRO registro. No cxGrid, Ctrl+Home vai ao
        # topo, entao nao dependemos do clique cair exatamente na 1a linha.
        ctrl_mais(VK_HOME)
        time.sleep(0.3)

        for _ in range(200):
            verificar_pausa()
            if not BOT_RODANDO:
                break

            # Zera o clipboard antes de copiar: se o Ctrl+C nao copiar
            # nada, detectamos isso em vez de reprocessar linha antiga.
            set_clipboard(SENTINELA_VAZIA)
            ctrl_mais(VK_C)
            time.sleep(0.3)
            texto = ler_clipboard()

            # Copia falhou (clipboard nao mudou) -> fim da grade
            if not texto or texto == SENTINELA_VAZIA:
                break

            # Salva o BRUTO do 1o Ctrl+C (com \t e \n visiveis) p/ diagnostico
            global _DEBUG_RAW_SALVO
            if not _DEBUG_RAW_SALVO:
                _DEBUG_RAW_SALVO = True
                try:
                    caminho_dbg = os.path.join(PASTA_ATUAL, "debug_clipboard.txt")
                    with open(caminho_dbg, "w", encoding="utf-8") as d:
                        d.write("Conteudo BRUTO do primeiro Ctrl+C (repr):\n\n")
                        d.write(repr(texto))
                except Exception:
                    pass

            # Linha identica a anterior -> grade nao avancou, evita loop
            if texto == ultimo_texto:
                break
            ultimo_texto = texto

            dados = parse_linha_grid(texto)
            if not dados:
                break

            tipo = dados["tipo"].lower()
            if "final" in tipo:
                break
            if tipo == "":
                break

            linhas_lidas.append(dados)
            tecla(VK_DOWN)
            time.sleep(0.2)

    except Exception as e:
        print(f"       [ERRO navegar_grade] {e}")

    return linhas_lidas

# ============================================================
# GERAR EXCEL
# ============================================================
def gerar_excel(linhas, resultados, caminho):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Almox"
    cabecalhos = [
        "Codigo", "Descricao", "Dept Cod", "Dept Nome",
        "Data", "Requisicao", "Quantidade", "Unidade",
        "Valor Unitario", "Valor Total"
    ]
    ws.append(cabecalhos)
    for item in linhas:
        chave = (item["codigo"], item["data"])
        val_unit = resultados.get(chave, item["val_unit"])
        ws.append([
            item["codigo"], item["descricao"], item["dept_codigo"],
            item["dept_nome"], item["data"], item["req"],
            item["qtd"], item["unidade"], val_unit, item["val_total"],
        ])
    wb.save(caminho)
    print(f"  Planilha salva: {caminho}")

# ============================================================
# INTERFACE
# ============================================================
def perguntar_quantidade(total):
    print(f"  Total de codigos encontrados no PDF: {total}")
    resp = input("  Quantos codigos processar? (Enter = todos): ").strip()
    if resp == "":
        return total
    try:
        n = int(resp)
        return min(n, total)
    except:
        return total

# ============================================================
# MAIN
# ============================================================
os.system("cls" if os.name == "nt" else "clear")
print("=" * 55)
print("  BOT ALMOX - Captura de Unitarios")
print("=" * 55)
print()

print("[1/5] Selecione o arquivo PDF...")
PDF_PATH = selecionar_pdf()
if not PDF_PATH:
    print("  Nenhum PDF selecionado. Encerrando.")
    input("Pressione ENTER para sair...")
    sys.exit(0)
print(f"  PDF: {os.path.basename(PDF_PATH)}")
print()

try:
    print("Lendo PDF...")
    linhas = ler_pdf(PDF_PATH)
    print(f"  Codigos encontrados no PDF (contando repetidos): {len(linhas)}")
    print(f"  Codigos distintos: {len(codigos_unicos(linhas))}")
    print()

    print("[2/5] Quantos codigos processar?")
    qtd = perguntar_quantidade(len(linhas))
    # Recorta os PRIMEIROS N codigos encontrados (linhas do PDF), na ordem.
    # A planilha final sera um espelho dessas linhas.
    linhas = linhas[:qtd]
    # A automacao busca cada codigo DISTINTO uma vez no MEGA (buscar o mesmo
    # codigo repetido daria o mesmo resultado). Esse e o numero de buscas.
    codigos = codigos_unicos(linhas)
    print(f"  Codigos a processar (contando repetidos): {len(linhas)}")
    print(f"  >> A automacao vai fazer {len(codigos)} buscas no MEGA (codigos distintos)")
    print()

    print("[3/5] Pronto!")
    print()

    print("[4/5] Iniciando automacao...")
    print("  Deixe a janela de consulta do MEGA ERP aberta e visivel.")
    print("  [F8] = Pausar / Retomar    [ESC] = Abortar (salva o que ja foi lido)")
    print("  Iniciando em 5 segundos...")
    time.sleep(5)
    print()

    print("[5/5] Executando...")
    print()

    LOG_PATH = os.path.join(PASTA_ATUAL, "log_captura_grid.txt")
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        log.write("LOG DE CAPTURA DA GRADE - ALMOX BOT\n")
        log.write("=" * 60 + "\n\n")

    linhas_por_codigo = {}
    for item in linhas:
        c = item["codigo"]
        if c not in linhas_por_codigo:
            linhas_por_codigo[c] = []
        linhas_por_codigo[c].append(item)

    resultados = {}

    for i, codigo in enumerate(codigos, 1):
        verificar_pausa()
        if not BOT_RODANDO:
            break

        codigo_limpo = codigo.replace(".", "")
        print(f"  [{i}/{len(codigos)}] Codigo: {codigo} -> digitando: {codigo_limpo}")

        print("    [passo 1] Digitando codigo...")
        clicar(*EDIT_COORDS)
        time.sleep(0.3)
        ctrl_mais(VK_A)
        time.sleep(0.1)
        tecla(VK_DELETE)
        time.sleep(0.1)
        digitar(codigo_limpo)
        time.sleep(0.3)

        print("    [passo 2] Clicando Filtrar...")
        clicar(*FILTRAR_COORDS)
        time.sleep(2)

        print("    [passo 3] Navegando grade...")
        linhas_grid = navegar_grade()
        print(f"    -> Linhas lidas: {len(linhas_grid)}")

        for lg in linhas_grid:
            print(f"       Tipo: {lg['tipo']} | Data: {lg['data']} | Vl.Saida: {lg['vl_saida']}")

        print("    [passo 4] Match por data...")
        for item in linhas_por_codigo.get(codigo, []):
            data_pdf = item["data"]
            preco = "#N/D"
            for lg in linhas_grid:
                # sem_acento resolve "Saída" vs "saida" (o tipo vem com acento)
                if lg["data"] == data_pdf and "saida" in sem_acento(lg["tipo"]):
                    preco = lg["vl_saida"]
                    break
            chave = (codigo, data_pdf)
            resultados[chave] = preco
            print(f"    -> Data PDF: {data_pdf} | Preco: {preco}")

        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"=== Codigo: {codigo} ===\n")
            for lg in linhas_grid:
                log.write(f"  tipo={lg['tipo']} data={lg['data']} vl={lg['vl_saida']}\n")
            log.write("=" * 40 + "\n\n")

    print()
    print("Gerando planilha final...")
    # A planilha ESPELHA o PDF: mesmas colunas, mesmas linhas na mesma
    # ordem, com o Valor Unitario preenchido pelo valor de saida da data
    # de cada linha.
    gerar_excel(linhas, resultados, EXCEL_PATH)
    print(f"  Linhas na planilha: {len(linhas)} (espelho das linhas do PDF processadas)")

    print()
    print("=" * 55)
    print("  FINALIZADO!")
    print(f"  Codigos processados (contando repetidos): {len(linhas)}")
    print(f"  Buscas feitas no MEGA (codigos distintos): {len(codigos)}")
    print(f"  Planilha: {EXCEL_PATH}")
    print(f"  Log da grid: {LOG_PATH}")
    print("=" * 55)

except Exception as e:
    print(f"\n\nERRO NA EXECUCAO: {e}")
    traceback.print_exc()
    salvar_crash("EXCEPT_MAIN", str(e))
    print(f"Erro salvo em: {ARQUIVO_CRASH}")

print()
input("Pressione ENTER para fechar...")
