import time
import RPi.GPIO as GPIO
import signal
import sys

def signal_handler(_sig, _frame):
    GPIO.cleanup()
    print('\nProgramm wird beendet.')    
    sys.exit(0)

# Signale registrieren (SIGINT = Ctrl+C, SIGTERM = Abbruchbefehl)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(37, GPIO.OUT)
    GPIO.setup(38, GPIO.OUT)
    GPIO.output(37, True)
    GPIO.output(38, True)
    while True:
        input(".")
        print("Schranke fährt hoch.")
        GPIO.output(37, False)
        time.sleep(1)
        print("Schranke ist oben.")
        GPIO.output(37, True)
        input(".")
        print("Schranke fährt runter.")
        GPIO.output(38, False)
        time.sleep(1)
        print("Schranke ist unten.")
        GPIO.output(38, True)
