import time, ctypes, sys
from ctypes import wintypes

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

user32 = ctypes.windll.user32
log_path = "teste_win32.txt"

with open(log_path, "w", encoding="utf-8") as f:
    f.write("TESTE BACKEND WIN32\n")
    f.write("=" * 60 + "\n\n")

def log_print(texto):
    print(texto)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(texto + "\n")

log_print("INSTRUCOES:")
log_print("1. Deixe a grade do MEGA ERP com resultados visivel")
log_print("2. Posicione o mouse sobre o texto 'saida' na grade")
log_print("3. Pressione F8 para testar backend win32")
log_print("4. Pressione F9 para testar screenshot + pixel")
log_print("5. Pressione ESC para sair")
log_print("")

while True:
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))

    # F8: win32 backend
    if user32.GetAsyncKeyState(0x77) & 0x8000:
        log_print(f"\n=== F8 em X:{pt.x} Y:{pt.y} ===")
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="win32")
            elem = desktop.from_point(pt.x, pt.y)
            log_print(f"  Text: '{elem.window_text()}'")
            log_print(f"  Class: {elem.class_name()}")
            log_print(f"  CtrlType: {elem.element_info.control_type}")
            
            # Tenta pegar todos os filhos
            try:
                filhos = elem.children()
                log_print(f"  Filhos diretos: {len(filhos)}")
                for i, child in enumerate(filhos[:20]):
                    txt = child.window_text() or "(vazio)"
                    cls = child.class_name() or "?"
                    log_print(f"  [{i}] text='{txt[:60]}' class={cls}")
            except Exception as e:
                log_print(f"  Erro filhos: {e}")
            
            # Tenta texts()
            try:
                textos = elem.texts()
                log_print(f"  texts(): {textos[:10]}")
            except Exception as e:
                log_print(f"  Erro texts(): {e}")
                
        except Exception as e:
            log_print(f"  Erro: {e}")
        time.sleep(0.5)

    # F9: screenshot + analise pixel
    if user32.GetAsyncKeyState(0x78) & 0x8000:
        log_print(f"\n=== F9 em X:{pt.x} Y:{pt.y} ===")
        try:
            # Tenta usar pyautogui para capturar o que tem na tela
            import pyautogui
            # Captura a regiao ao redor do cursor
            regiao = (pt.x - 100, pt.y - 50, 300, 200)
            img = pyautogui.screenshot(region=regiao)
            img.save("regiao_grade.png")
            log_print(f"  Screenshot salvo: regiao_grade.png")
            log_print(f"  Regiao: X:{regiao[0]} Y:{regiao[1]} W:{regiao[2]} H:{regiao[3]}")
            log_print(f"  Tamanho: {img.size}")
        except Exception as e:
            log_print(f"  Erro: {e}")
        time.sleep(0.5)

    # ESC
    if user32.GetAsyncKeyState(0x1B) & 0x8000:
        log_print("\nEncerrando...")
        break

    time.sleep(0.05)

log_print(f"\nLog salvo: {log_path}")
input("Pressione ENTER para fechar...")
