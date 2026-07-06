"""
comparar_pdf_planilha.py - Confere se TODOS os itens do PDF estao na planilha

Le o PDF de codigos e o resultados_almox.xlsx gerado pelo bot e compara,
por (codigo, data), o que esta faltando ou sobrando na planilha.

USO:
  1) Deixe o PDF e o resultados_almox.xlsx na mesma pasta.
  2) python comparar_pdf_planilha.py
  3) Selecione o PDF quando pedir (ou ajuste PDF_PATH abaixo).

Requer: pypdf (ou PyPDF2), openpyxl
"""

import os
import re
from collections import Counter
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
import openpyxl
import tkinter as tk
from tkinter import filedialog

PASTA = os.path.dirname(__file__) or "."
XLSX_PATH = os.path.join(PASTA, "resultados_almox.xlsx")


# Mesma logica de parse do almox_bot.py (so o que interessa: codigo e data)
def parse_linha(linha):
    partes = re.split(r"(\d{2}/\d{2}/\d{4})", linha)
    if len(partes) < 3:
        return None
    antes = partes[0].strip()
    data = partes[1].strip()
    m = re.match(r"^(\d{2}\.\d{3})", antes)
    if not m:
        return None
    return m.group(1), data


def ler_pdf(caminho):
    itens = []
    with open(caminho, "rb") as f:
        reader = PdfReader(f)
        for pagina in reader.pages:
            for linha in (pagina.extract_text() or "").split("\n"):
                linha = linha.strip()
                if not linha:
                    continue
                d = parse_linha(linha)
                if d:
                    itens.append(d)
    return itens


def ler_xlsx(caminho):
    itens = []
    wb = openpyxl.load_workbook(caminho, read_only=True)
    ws = wb.active
    primeira = True
    for row in ws.iter_rows(values_only=True):
        if primeira:  # pula cabecalho
            primeira = False
            continue
        if row is None or row[0] is None:
            continue
        codigo = str(row[0]).strip()
        data = str(row[4]).strip() if len(row) > 4 and row[4] is not None else ""
        itens.append((codigo, data))
    wb.close()
    return itens


def selecionar_pdf():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    c = filedialog.askopenfilename(
        title="Selecione o MESMO PDF usado na automacao",
        filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
    )
    root.destroy()
    return c


def main():
    print("=" * 60)
    print(" COMPARADOR  PDF  x  PLANILHA")
    print("=" * 60)

    if not os.path.exists(XLSX_PATH):
        print(f"\n[ERRO] Nao achei a planilha: {XLSX_PATH}")
        print("Rode o almox_bot.py primeiro (gera resultados_almox.xlsx).")
        return

    pdf_path = selecionar_pdf()
    if not pdf_path:
        print("Nenhum PDF selecionado.")
        return

    pdf_itens = ler_pdf(pdf_path)
    xls_itens = ler_xlsx(XLSX_PATH)

    pdf_cont = Counter(pdf_itens)
    xls_cont = Counter(xls_itens)

    pdf_cods = set(c for c, _ in pdf_itens)
    xls_cods = set(c for c, _ in xls_itens)

    print(f"\nPDF   : {len(pdf_itens)} linhas | {len(pdf_cods)} codigos | {len(set(pdf_itens))} pares (cod,data)")
    print(f"XLSX  : {len(xls_itens)} linhas | {len(xls_cods)} codigos | {len(set(xls_itens))} pares (cod,data)")

    # 1) Codigos que estao na planilha mas NAO no PDF (nao deveria acontecer)
    cods_extra = xls_cods - pdf_cods
    print(f"\n[1] Codigos na planilha que NAO existem no PDF: {len(cods_extra)}")
    for c in sorted(cods_extra)[:30]:
        print(f"    EXTRA: {c}")

    # 2) Considera SO os codigos que estao na planilha (voce pode ter
    #    limitado o teste a N codigos). Para esses, confere se todas as
    #    linhas do PDF aparecem na planilha.
    print(f"\n[2] Conferindo integridade dos codigos presentes na planilha...")
    faltando = []   # (codigo, data, qtd_pdf, qtd_xlsx)
    sobrando = []
    for chave, qpdf in pdf_cont.items():
        cod, _ = chave
        if cod not in xls_cods:
            continue  # codigo nao processado neste teste; ignora
        qxls = xls_cont.get(chave, 0)
        if qxls < qpdf:
            faltando.append((chave, qpdf, qxls))
        elif qxls > qpdf:
            sobrando.append((chave, qpdf, qxls))

    print(f"    Pares FALTANDO na planilha : {len(faltando)}")
    for (c, dt), qp, qx in faltando[:40]:
        print(f"       FALTA  {c} {dt}  (PDF={qp}  XLSX={qx})")

    print(f"    Pares SOBRANDO na planilha : {len(sobrando)}")
    for (c, dt), qp, qx in sobrando[:40]:
        print(f"       SOBRA  {c} {dt}  (PDF={qp}  XLSX={qx})")

    # 3) Codigos do PDF que nao entraram na planilha (esperado se limitou teste)
    cods_nao_processados = pdf_cods - xls_cods
    print(f"\n[3] Codigos do PDF que NAO estao na planilha: {len(cods_nao_processados)}")
    print(f"    (normal se voce limitou o teste a poucos codigos)")

    print("\n" + "=" * 60)
    if not cods_extra and not faltando and not sobrando:
        print(" RESULTADO: OK! Todos os itens dos codigos processados batem.")
    else:
        print(" RESULTADO: Ha divergencias acima. Me mande esta saida.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        input("\nPressione ENTER para fechar...")
