import json
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

# Inicializa os controladores
mouse = MouseController()
keyboard = KeyboardController()

# Carrega os eventos do arquivo JSON
with open('inputs.json', 'r') as f:
    events = json.load(f)

print("⏳ Executando em 3 segundos...")
time.sleep(3)

for event in events:
    delay = event['time']
    time.sleep(delay)  # Espera entre eventos

    if event['type'] == 'mouse_click':
        pos = event['data']['position']
        button_str = event['data']['button']
        action = event['data']['action']

        # Converte string para botão real
        button = Button.left if 'left' in button_str else Button.right

        mouse.position = tuple(pos)
        if action == 'pressed':
            mouse.press(button)
        elif action == 'released':
            mouse.release(button)

    elif event['type'] == 'key_press':
        key_val = event['data']['key']
        try:
            if len(key_val) == 1:
                keyboard.press(key_val)
                keyboard.release(key_val)
            else:
                key = getattr(Key, key_val.replace("Key.", ""))
                keyboard.press(key)
                keyboard.release(key)
        except Exception as e:
            print(f"[ERRO] ao pressionar tecla: {key_val} - {e}")

print("✅ Execução finalizada!")
