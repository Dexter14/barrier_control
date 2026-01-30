import signal
import sys
import time
import RPi.GPIO as GPIO

def signal_handler(_sig, _frame):
    GPIO.cleanup()
    print('\nProgramm wird beendet. Bereinigung läuft...')    
    sys.exit(0)

# Signale registrieren (SIGINT = Ctrl+C, SIGTERM = Abbruchbefehl)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(37, GPIO.OUT)
    GPIO.setup(38, GPIO.OUT)
    GPIO.setup(40, GPIO.OUT)
    GPIO.output(37, GPIO.HIGH)
    GPIO.output(38, GPIO.HIGH)
    GPIO.output(40, GPIO.HIGH)
    while True:
        input(".")
        print("Schranke fährt hoch.")
        GPIO.output(37, GPIO.LOW)
        time.sleep(1)
        print("Schranke ist oben.")
        GPIO.output(37, GPIO.HIGH)
        input(".")
        print("Schranke fährt runter.")
        GPIO.output(38, GPIO.LOW)
        time.sleep(1)
        print("Schranke ist unten.")
        GPIO.output(38, GPIO.HIGH)
