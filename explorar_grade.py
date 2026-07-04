import time
import ctypes
from ctypes import wintypes
from pywinauto import Desktop

user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

def dump_tree(elem, nivel=0, max_nivel=6):
    """Percorre a arvore UIA do elemento e retorna texto com todos os filhos."""
    if nivel > max_nivel:
        return ""
    tabs = "  " * nivel
    texto = elem.window_text() or "(sem texto)"
    cls = elem.class_name() or "(sem class)"
    ctrl = elem.element_info.control_type or "?"
    aid = elem.element_info.automation_id or "?"
    saida = f"{tabs}[{ctrl}] Class={cls} Aid={aid} Text='{texto[:60]}'\n"
    try:
        for filho in elem.children():
            saida += dump_tree(filho, nivel + 1, max_nivel)
    except:
        saida += f"{tabs}  (erro ao acessar filhos)\n"
    return saida

def dump_grid_info(elem):
    """Tenta extrair todas as celulas visiveis da grade."""
    saida = ""
    try:
        for filho in elem.descendants():
            txt = filho.window_text() or ""
            if txt.strip():
                cls = filho.class_name() or "?"
                ctrl = filho.element_info.control_type or "?"
                aid = filho.element_info.automation_id or "?"
                saida += f"  Ctrl={ctrl} Class={cls} Aid={aid} Text='{txt[:80]}'\n"
    except:
        saida += "  (erro ao percorrer descendentes)\n"
    return saida

def main():
    print("=" * 70)
    print(" EXPLORADOR DE GRADE DO MEGA ERP")
    print("=" * 70)
    print()
    print(" Instrucoes:")
    print("  [F8]   = Capturar elemento + arvore completa")
    print("  [F9]   = Dump de TODAS as celulas visiveis da grade")
    print("  [F10]  = Busca por 'saida' em toda a arvore")
    print("  [ESC]  = Sair")
    print()
    print(" Dica: Aponte o mouse para a grade (TMgCxGrid) e pressione F9")
    print()

    desktop = Desktop(backend="uia")
    log_path = "exploracao_grade.txt"

    while True:
        # F8 - captura elemento + arvore
        if user32.GetAsyncKeyState(0x77) & 0x8000:
            try:
                pt = POINT()
                user32.GetCursorPos(ctypes.byref(pt))
                x, y = pt.x, pt.y
                print(f"\n=== F8 em X:{x} Y:{y} ===")
                elem = desktop.from_point(x, y)

                info = f"\n=== CAPTURA F8 em {time.strftime('%H:%M:%S')} (X:{x} Y:{y}) ===\n"
                info += f"  Title    : '{elem.window_text()}'\n"
                info += f"  ClassName: '{elem.class_name()}'\n"
                info += f"  CtrlType : '{elem.element_info.control_type}'\n"
                info += f"  AutoId   : '{elem.element_info.automation_id}'\n"

                try:
                    pai = elem.parent()
                    info += f"  Pai      : Class={pai.class_name()} Ctrl={pai.element_info.control_type} Aid={pai.element_info.automation_id}\n"
                except:
                    pass

                info += "\n--- Arvore completa a partir do elemento ---\n"
                info += dump_tree(elem, 1)

                print(info)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(info)
                print(f"  (salvo em {log_path})")
                time.sleep(0.5)

            except Exception as e:
                print(f"  ERRO: {e}")
            time.sleep(0.3)

        # F9 - dump de celulas da grade
        if user32.GetAsyncKeyState(0x78) & 0x8000:
            try:
                pt = POINT()
                user32.GetCursorPos(ctypes.byref(pt))
                x, y = pt.x, pt.y
                print(f"\n=== F9 - Dump de celulas X:{x} Y:{y} ===")
                elem = desktop.from_point(x, y)

                info = f"\n=== DUMP GRADE em {time.strftime('%H:%M:%S')} (X:{x} Y:{y}) ===\n"
                info += f"  Elemento alvo: Class={elem.class_name()} Ctrl={elem.element_info.control_type}\n"
                info += "\n--- Todas as celulas com texto visivel ---\n"
                info += dump_grid_info(elem)

                print(info)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(info)
                print(f"  (salvo em {log_path})")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ERRO: {e}")

        # F10 - busca por "saida"
        if user32.GetAsyncKeyState(0x79) & 0x8000:
            try:
                pt = POINT()
                user32.GetCursorPos(ctypes.byref(pt))
                x, y = pt.x, pt.y
                print(f"\n=== F10 - Busca por 'saida' em X:{x} Y:{y} ===")
                elem = desktop.from_point(x, y)

                info = f"\n=== BUSCA SAIDA em {time.strftime('%H:%M:%S')} (X:{x} Y:{y}) ===\n"
                info += f"  Elemento alvo: Class={elem.class_name()} Ctrl={elem.element_info.control_type}\n"
                info += "\n--- Elementos contendo 'saida' ---\n"

                try:
                    for filho in elem.descendants():
                        txt = filho.window_text() or ""
                        if "saida" in txt.lower():
                            cls = filho.class_name() or "?"
                            ctrl = filho.element_info.control_type or "?"
                            aid = filho.element_info.automation_id or "?"
                            info += f"  Ctrl={ctrl} Class={cls} Aid={aid} Text='{txt[:80]}'\n"
                except:
                    info += "  (erro na busca)\n"

                print(info)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(info)
                print(f"  (salvo em {log_path})")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ERRO: {e}")

        # ESC - sair
        if user32.GetAsyncKeyState(0x1B) & 0x8000:
            print("\nEncerrando...")
            break

        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro fatal: {e}")
    finally:
        print()
        print(f"Log salvo em: exploracao_grade.txt")
        input("Pressione ENTER para fechar...")
