import numpy as np
import time
import random
from robot_hand_controller import servos, leer_distancia

# === Configuración del agente ===
actions = list(range(len(servos)))  # Cada servo es una acción
states = ['rest', 'stimulus_near', 'stimulus_far']  # Estado basado en sensor
q_table = np.zeros((len(states), len(actions)))

learning_rate = 0.1
discount_factor = 0.95
exploration_rate = 0.2

def get_state(distancia):
    if distancia < 10:
        return 1  # 'stimulus_near'
    elif distancia > 25:
        return 2  # 'stimulus_far'
    else:
        return 0  # 'rest'

def apply_action(action):
    servos[action].min()
    time.sleep(0.3)
    servos[action].max()
    time.sleep(0.3)
    servos[action].mid()

def get_reward(estado_actual):
    # Suponemos que si el estímulo está lejos, queremos atraer al Physarum
    if estado_actual == 2:
        return 1
    elif estado_actual == 1:
        return -1
    return 0

# === Bucle de entrenamiento ===
print("Entrenando al agente de Physarum...")
try:
    for episode in range(500):  # Número de iteraciones
        distancia = leer_distancia()
        state_idx = get_state(distancia)

        if random.uniform(0, 1) < exploration_rate:
            action = random.choice(actions)
        else:
            action = np.argmax(q_table[state_idx])

        apply_action(action)
        time.sleep(1)

        new_distancia = leer_distancia()
        new_state_idx = get_state(new_distancia)
        reward = get_reward(new_state_idx)

        # Actualizar Q-table
        old_value = q_table[state_idx, action]
        future_max = np.max(q_table[new_state_idx])
        new_value = (1 - learning_rate) * old_value + learning_rate * (reward + discount_factor * future_max)
        q_table[state_idx, action] = new_value

        print(f"Episodio {episode+1} | Estado: {states[state_idx]} | Acción: Servo {action} | Recompensa: {reward}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Entrenamiento detenido por el usuario.")
