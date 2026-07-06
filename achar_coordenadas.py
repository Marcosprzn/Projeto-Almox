"""
achar_coordenadas.py - Recalibra as coordenadas do bot na SUA tela

O bot clica em posicoes de pixel fixas (campo do codigo, botao Filtrar,
primeiro item da grade). Se a janela do MEGA estiver em outra posicao ou
resolucao, esses cliques caem no lugar errado ("clica em algo a mais").

Este utilitario mostra a posicao do mouse AO VIVO e captura os 3 pontos
que o bot precisa. No final, imprime o bloco pronto para colar no
almox_bot.py.

COMO USAR:
  1) Abra o MEGA na tela de consulta (campo de codigo + grade visiveis).
  2) Rode:  python achar_coordenadas.py
  3) Para cada alvo pedido, posicione o mouse EXATAMENTE em cima e
     pressione F8. (ESC cancela.)
  4) Copie o bloco final para o topo do almox_bot.py.
"""

import time
import ctypes
import sys
from ctypes import wintypes


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


user32 = ctypes.windll.user32
VK_F8 = 0x77
VK_ESC = 0x1B


def pos_mouse():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def capturar(nome, descricao):
    """Espera o F8 e devolve a posicao do mouse naquele instante."""
    print(f"\n>> {nome}")
    print(f"   Posicione o mouse sobre: {descricao}")
    print(f"   e pressione F8 (ou ESC para cancelar)...")
    while True:
        x, y = pos_mouse()
        # \r reescreve a mesma linha (posicao ao vivo)
        sys.stdout.write(f"\r   mouse -> X:{x:<5} Y:{y:<5}   ")
        sys.stdout.flush()

        if user32.GetAsyncKeyState(VK_F8) & 0x8000:
            print(f"\n   [OK] {nome} = ({x}, {y})")
            time.sleep(0.4)  # evita capturar o mesmo F8 duas vezes
            return (x, y)

        if user32.GetAsyncKeyState(VK_ESC) & 0x8000:
            print("\n   Cancelado.")
            return None

        time.sleep(0.03)


def main():
    print("=" * 60)
    print(" RECALIBRAR COORDENADAS DO ALMOX BOT")
    print("=" * 60)
    print(" Deixe a janela do MEGA visivel e va apontando o mouse.")

    alvos = [
        ("EDIT_COORDS",    "o CAMPO onde se digita o codigo"),
        ("FILTRAR_COORDS", "o BOTAO Filtrar"),
        ("PRIMEIRA_LINHA", "o PRIMEIRO item da tabela/grade"),
    ]

    resultado = {}
    for nome, desc in alvos:
        ponto = capturar(nome, desc)
        if ponto is None:
            print("\nOperacao cancelada. Nada foi salvo.")
            return
        resultado[nome] = ponto

    print("\n" + "=" * 60)
    print(" PRONTO! Copie estas 3 linhas para o topo do almox_bot.py")
    print(" (substituindo as que ja existem la):")
    print("=" * 60)
    print()
    print(f"EDIT_COORDS       = {resultado['EDIT_COORDS']}")
    print(f"FILTRAR_COORDS    = {resultado['FILTRAR_COORDS']}")
    print(f"PRIMEIRA_LINHA    = {resultado['PRIMEIRA_LINHA']}  # Primeiro item da tabela")
    print()

    # Salva tambem em arquivo, por conveniencia
    with open("coordenadas_novas.txt", "w", encoding="utf-8") as f:
        f.write(f"EDIT_COORDS       = {resultado['EDIT_COORDS']}\n")
        f.write(f"FILTRAR_COORDS    = {resultado['FILTRAR_COORDS']}\n")
        f.write(f"PRIMEIRA_LINHA    = {resultado['PRIMEIRA_LINHA']}  # Primeiro item da tabela\n")
    print(" (tambem salvo em coordenadas_novas.txt)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nErro: {e}")
    finally:
        input("\nPressione ENTER para fechar...")
