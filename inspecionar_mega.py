"""
inspecionar_mega.py - Descobre os controles reais da janela do Mega ERP

Objetivo: parar de clicar em coordenadas de pixel e passar a mirar os
controles pelo nome/classe (campo de codigo, botao Filtrar, grade).

COMO USAR:
  1) Abra o Mega e deixe a tela de consulta (com o campo de codigo e a
     grade) visivel.
  2) Rode este script:  python inspecionar_mega.py
  3) ETAPA 1 lista todas as janelas abertas -> ache a do Mega e copie um
     pedaco do titulo dela.
  4) Cole esse pedaco quando o script pedir.
  5) ETAPA 2 imprime a arvore de controles daquela janela e salva em
     'inspecao_mega.txt'. Me mande esse arquivo.

Requer:  pip install pywinauto
"""

import time
from pywinauto import Desktop

LOG = "inspecao_mega.txt"


def salvar(texto):
    print(texto)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(texto + "\n")


def listar_janelas():
    salvar("=" * 70)
    salvar(" ETAPA 1 - Janelas abertas (procure a do Mega)")
    salvar("=" * 70)
    janelas = Desktop(backend="uia").windows()
    vistos = set()
    for w in janelas:
        try:
            titulo = w.window_text().strip()
            cls = w.class_name()
            if not titulo:
                continue
            chave = (titulo, cls)
            if chave in vistos:
                continue
            vistos.add(chave)
            salvar(f"  titulo='{titulo[:60]}'  |  classe={cls}")
        except Exception:
            continue


def dump_controles(trecho_titulo):
    salvar("")
    salvar("=" * 70)
    salvar(f" ETAPA 2 - Controles da janela contendo '{trecho_titulo}'")
    salvar("=" * 70)

    # Tenta primeiro backend uia, depois win32 (Delphi as vezes responde
    # melhor a um deles).
    for backend in ("uia", "win32"):
        try:
            salvar(f"\n----- Tentando backend '{backend}' -----")
            janela = Desktop(backend=backend).window(title_re=f".*{trecho_titulo}.*")
            janela.wait("exists ready", timeout=10)

            # print_control_identifiers escreve no stdout; capturamos
            # redirecionando para o arquivo tambem.
            salvar(f"[janela encontrada: '{janela.window_text()}' classe={janela.class_name()}]")
            with open(LOG, "a", encoding="utf-8") as f:
                # profundidade limitada p/ nao explodir em telas gigantes
                janela.print_control_identifiers(depth=None, filename=None)
                # print_control_identifiers imprime no console; replicamos:
            # Captura textual alternativa (descendentes com texto)
            salvar("\n--- Descendentes com texto/classe relevante ---")
            for ctrl in janela.descendants():
                try:
                    txt = (ctrl.window_text() or "").strip()
                    cls = ctrl.class_name() or ""
                    # foca no que interessa: edits, botoes e a grade
                    interessa = (
                        "Edit" in cls or "Button" in cls or "Grid" in cls
                        or "cx" in cls.lower() or txt.lower() in ("filtrar", "filtro")
                    )
                    if interessa:
                        aid = ctrl.element_info.automation_id
                        ctp = ctrl.element_info.control_type
                        salvar(f"  classe={cls:<28} tipo={ctp:<12} aid={aid!r:<14} text='{txt[:40]}'")
                except Exception:
                    continue
            salvar(f"\n[OK backend {backend}] Salvo em {LOG}")
            return
        except Exception as e:
            salvar(f"  [falhou no backend {backend}] {e}")

    salvar("Nao consegui conectar. Confira o trecho do titulo e se a janela esta aberta.")


if __name__ == "__main__":
    # limpa log
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("INSPECAO DA JANELA DO MEGA ERP\n")
        f.write("=" * 70 + "\n\n")

    listar_janelas()

    print("\n" + "=" * 70)
    trecho = input("Digite um trecho do TITULO da janela do Mega: ").strip()
    if trecho:
        dump_controles(trecho)
    else:
        print("Nenhum titulo informado. Encerrando.")

    print(f"\nPronto. Me envie o arquivo: {LOG}")
    input("Pressione ENTER para fechar...")
