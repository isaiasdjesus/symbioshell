from gpiozero import Servo
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import threading
import datetime

# === CONFIGURACIÓN DE PINES ===
servo_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
servos = []

# Configurar servos (suponiendo señal PWM con gpiozero)
for pin in servo_pins:
    servo = Servo(pin)
    servos.append(servo)

# HC-SR04: Pines
TRIG = 17
ECHO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Cámara
camera = PiCamera()
camera.rotation = 180
camera.resolution = (1024, 768)

# === FUNCIONES ===

def mover_dedo(servo):
    try:
        servo.min()
        time.sleep(0.5)
        servo.max()
        time.sleep(0.5)
        servo.mid()
    except:
        print("Error en movimiento del servo")

def mover_todos_los_dedos():
    for servo in servos:
        mover_dedo(servo)
        time.sleep(0.3)

def leer_distancia():
    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Velocidad sonido ida y vuelta
    distance = round(distance, 2)
    return distance

def loop_sensor():
    while True:
        distancia = leer_distancia()
        print(f"[{datetime.datetime.now()}] Distancia: {distancia} cm")
        time.sleep(10)

def tomar_foto_cada_5_horas():
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"/home/pi/fotos/foto_{timestamp}.jpg"
        camera.capture(filename)
        print(f"Foto tomada: {filename}")
        time.sleep(18000)  # 5 horas en segundos

# === INICIO DE HILOS Y MAIN ===

if __name__ == "__main__":
    try:
        print("Iniciando sistema...")
        threading.Thread(target=loop_sensor, daemon=True).start()
        threading.Thread(target=tomar_foto_cada_5_horas, daemon=True).start()
        
        while True:
            mover_todos_los_dedos()
            time.sleep(15)

    except KeyboardInterrupt:
        print("Saliendo...")
        GPIO.cleanup()
