import tkinter as tk
from threading import Thread
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import keyboard as kb
import json
import time
import ctypes

# Variáveis globais
recording = False
events = []
start_time = None
stop_flag = False

# --- Suporte nativo a Mouse4 e Mouse5 ---
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

def click_mouse_xbutton(button, action):
    if button == 'x1':
        xbtn = XBUTTON1
    elif button == 'x2':
        xbtn = XBUTTON2
    else:
        return

    if action == 'pressed':
        flags = MOUSEEVENTF_XDOWN
    else:
        flags = MOUSEEVENTF_XUP

    ctypes.windll.user32.mouse_event(flags, 0, 0, xbtn, 0)

# --- Gravação de eventos ---
def log_event(event_type, data):
    global start_time
    current_time = time.time()
    if start_time is None:
        start_time = current_time
    delta = current_time - start_time
    start_time = current_time
    events.append({'type': event_type, 'data': data, 'time': delta})

def on_click(x, y, button, pressed):
    if recording:
        action = 'pressed' if pressed else 'released'
        if hasattr(button, 'name'):
            btn_str = button.name.lower()
        else:
            btn_str = str(button).lower()
        log_event('mouse_click', {
            'button': btn_str,
            'action': action,
            'position': (x, y)
        })

def on_press(key):
    global recording, events, start_time
    if key == Key.f8:
        start_time = None
        events.clear()
        set_status("🎙️ Gravando... (F9 para parar)")
        globals()['recording'] = True
    elif key == Key.f9:
        globals()['recording'] = False
        with open('inputs.json', 'w') as f:
            json.dump(events, f, indent=2)
        set_status("💾 Gravação salva em inputs.json")
        return False
    elif recording:
        try:
            log_event('key_press', {'key': key.char})
        except AttributeError:
            log_event('key_press', {'key': str(key)})

def gravar_eventos():
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    keyboard_listener.start()
    keyboard_listener.join()

# --- ESC Listener com keyboard ---
def esc_listener():
    global stop_flag
    while not stop_flag:
        if kb.is_pressed("esc"):
            stop_flag = True
            set_status("⛔ Execução interrompida pelo usuário.")
            break
        time.sleep(0.1)

# --- Reprodução dos eventos ---
def reproduzir_com_intervalo():
    global stop_flag
    stop_flag = False

    try:
        with open('inputs.json', 'r') as f:
            eventos = json.load(f)
    except FileNotFoundError:
        set_status("❌ Arquivo inputs.json não encontrado!")
        return

    try:
        intervalo = int(entry_intervalo.get())
        if intervalo <= 0:
            raise ValueError
    except ValueError:
        set_status("❌ Intervalo inválido!")
        return

    mouse_ctrl = MouseController()
    keyboard_ctrl = KeyboardController()

    set_status("⏳ Iniciando em 3 segundos...")
    time.sleep(3)

    Thread(target=esc_listener, daemon=True).start()

    loop_count = 1
    while not stop_flag:
        set_status(f"🔁 Executando comandos (loop #{loop_count})... (ESC para parar)")
        loop_count += 1

        for e in eventos:
            if stop_flag:
                break
            time.sleep(e['time'])

            if e['type'] == 'mouse_click':
                pos = e['data']['position']
                btn_str = e['data']['button'].lower()
                mouse_ctrl.position = tuple(pos)

                if btn_str in ('left', 'right', 'middle'):
                    btn = getattr(Button, btn_str)
                    if e['data']['action'] == 'pressed':
                        mouse_ctrl.press(btn)
                    else:
                        mouse_ctrl.release(btn)

                elif btn_str in ('x_button1', 'button8', 'x1'):
                    click_mouse_xbutton('x1', e['data']['action'])

                elif btn_str in ('x_button2', 'button9', 'x2'):
                    click_mouse_xbutton('x2', e['data']['action'])

                else:
                    print(f"[WARN] Botão de mouse não reconhecido: {btn_str}")

            elif e['type'] == 'key_press':
                key_val = e['data']['key']
                try:
                    if len(key_val) == 1:
                        keyboard_ctrl.press(key_val)
                        keyboard_ctrl.release(key_val)
                    else:
                        key = getattr(Key, key_val.replace("Key.", ""))
                        keyboard_ctrl.press(key)
                        keyboard_ctrl.release(key)
                except Exception as err:
                    print(f"Erro na tecla {key_val}: {err}")

        if stop_flag:
            break

        # ⏳ Contador regressivo
        for remaining in range(intervalo, 0, -1):
            if stop_flag:
                break
            set_status(f"⏳ Próxima execução em: {remaining}s (ESC para parar)")
            time.sleep(1)

    set_status("✅ Execução finalizada ou interrompida.")

# --- Interface gráfica ---
def set_status(msg):
    status_var.set(msg)
    status_label.update_idletasks()

def start_gravacao():
    Thread(target=gravar_eventos, daemon=True).start()

def start_reproducao():
    Thread(target=reproduzir_com_intervalo, daemon=True).start()

# GUI
root = tk.Tk()
root.title("AutoClicker Intervalado")

status_var = tk.StringVar()
status_var.set("Pronto")

tk.Label(root, text="AutoClicker com Intervalo + Mouse4/5 + ESC", font=("Arial", 14, "bold")).pack(pady=10)

btn_gravar = tk.Button(root, text="🎙️ Gravar (F8/F9)", font=("Arial", 12), width=30, command=start_gravacao)
btn_gravar.pack(pady=10)

frame_intervalo = tk.Frame(root)
frame_intervalo.pack(pady=5)

tk.Label(frame_intervalo, text="Intervalo entre execuções (s):").pack(side=tk.LEFT, padx=5)
entry_intervalo = tk.Entry(frame_intervalo, width=6)
entry_intervalo.insert(0, "180")
entry_intervalo.pack(side=tk.LEFT)

btn_reproduzir = tk.Button(root, text="▶️ Iniciar Execução Intervalada", font=("Arial", 12), width=30, command=start_reproducao)
btn_reproduzir.pack(pady=10)

status_label = tk.Label(root, textvariable=status_var, fg="blue", font=("Arial", 10))
status_label.pack(pady=10)

root.mainloop()
