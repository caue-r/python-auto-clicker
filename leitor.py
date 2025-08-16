from pynput import mouse, keyboard
from pynput.keyboard import Key
import time
import json

# Variáveis de controle
recording = False
events = []
start_time = None

def log_event(event_type, data):
    global start_time
    current_time = time.time()
    if start_time is None:
        start_time = current_time
    delta = current_time - start_time
    start_time = current_time

    events.append({
        'type': event_type,
        'data': data,
        'time': delta
    })

# --- Mouse Handlers ---
def on_click(x, y, button, pressed):
    if recording:
        action = 'pressed' if pressed else 'released'
        log_event('mouse_click', {'button': str(button), 'action': action, 'position': (x, y)})

# --- Keyboard Handlers ---
def on_press(key):
    global recording, events, start_time

    if key == Key.f8:  # Início da gravação
        recording = True
        events = []
        start_time = None
        print("▶️ Gravando...")
    elif key == Key.f9:  # Fim da gravação
        recording = False
        print("⏹️ Gravação finalizada!")
        with open('inputs.json', 'w') as f:
            json.dump(events, f, indent=2)
        return False  # Para o listener
    elif recording:
        try:
            log_event('key_press', {'key': key.char})
        except AttributeError:
            log_event('key_press', {'key': str(key)})

# Setup dos listeners
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

keyboard_listener.join()
