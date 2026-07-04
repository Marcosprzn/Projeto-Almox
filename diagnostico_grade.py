import time
import ctypes
from ctypes import wintypes
from pywinauto import Desktop

user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

def texto_na_posicao(x, y, desktop):
    try:
        elem = desktop.from_point(x, y)
        txt = elem.window_text()
        cls = elem.class_name()
        ctrl = elem.element_info.control_type
        aid = elem.element_info.automation_id
        return txt.strip(), cls, ctrl, aid
    except Exception as e:
        return None, None, None, str(e)

def testar_posicoes():
    print("=" * 60)
    print(" DIAGNOSTICO DA GRADE - Teste de leitura")
    print("=" * 60)
    print()
    print(" Instrucoes:")
    print("  1. Abra o MEGA ERP e filtre um codigo")
    print("  2. Deixe a grade com resultados visivel")
    print("  3. Posicione o mouse sobre a grade")
    print("  4. Pressione F8 para testar varias posicoes")
    print("  5. Pressione ESC para sair")
    print()

    desktop = Desktop(backend="uia")
    log_path = "diagnostico_grade.txt"

    # Limpa log
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("DIAGNOSTICO DA GRADE\n")
        f.write("=" * 60 + "\n\n")

    while True:
        if user32.GetAsyncKeyState(0x77) & 0x8000:
            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            mx, my = pt.x, pt.y
            print(f"\n=== Testando posicoes a partir de X:{mx} Y:{my} ===")

            info = f"\n=== DIAGNOSTICO {time.strftime('%H:%M:%S')} (cursor X:{mx} Y:{my}) ===\n"
            info += f"{'Posicao':>15s} | {'Texto':<35s} | {'Classe':<25s} | {'Ctrl':<10s} | {'AutoId':<10s}\n"
            info += "-" * 110 + "\n"

            # Tenta pontos em cruz ao redor do cursor
            pontos = [(mx, my)]
            for dx in [0, 20, -20, 50, -50, 100, -100, 150, -150]:
                for dy in [0, 10, -10, 20, -20, 30, -30, 50, -50]:
                    if dx == 0 and dy == 0:
                        continue
                    pontos.append((mx + dx, my + dy))
                    if len(pontos) >= 30:
                        break
                if len(pontos) >= 30:
                    break

            for x, y in pontos:
                txt, cls, ctrl, aid = texto_na_posicao(x, y, desktop)
                txt_mostra = (txt[:35] if txt else "(vazio)") if txt is not None else "(erro)"
                cls_mostra = (cls[:25] if cls else "?")
                ctrl_mostra = (ctrl[:10] if ctrl else "?")
                aid_mostra = (aid[:10] if aid else "?")
                linha = f"({x:>4},{y:<4}) | {txt_mostra:<35s} | {cls_mostra:<25s} | {ctrl_mostra:<10s} | {aid_mostra:<10s}"
                info += linha + "\n"
                if txt and ("saida" in txt.lower() or "preco" in txt.lower() or txt.replace(",", "").replace(".", "").isdigit()):
                    print(f"  >>> ENCONTRADO: {txt} em ({x},{y}) Class={cls}")
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f">>> ENCONTRADO: '{txt}' em ({x},{y}) Class={cls} Ctrl={ctrl}\n")

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(info)
            print(f"  Log salvo em {log_path}")
            print(f"  (testadas {len(pontos)} posicoes)")
            time.sleep(0.5)

        if user32.GetAsyncKeyState(0x1B) & 0x8000:
            print("\nEncerrando...")
            break

        time.sleep(0.05)

if __name__ == "__main__":
    try:
        testar_posicoes()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print(f"\nLog completo: diagnostico_grade.txt")
        input("Pressione ENTER para fechar...")
