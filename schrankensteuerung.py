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

class BarrierControl:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(37, GPIO.OUT)
        GPIO.setup(38, GPIO.OUT)
        GPIO.setup(36, GPIO.IN)
        GPIO.output(37, True)
        GPIO.output(38, True)
        self.status = "down"

    def move_barrier(self, _channel):
        if "down" == self.status:
            self.move_up(2)
        elif "up" == self.status:
            self.move_down(2)
        else:
           raise ValueError


    def move_up(self, delay):
        print("Schranke fährt hoch.")
        GPIO.output(37, False)
        time.sleep(delay)
        print("Schranke ist oben.")
        GPIO.output(37, True)
        self.status = "up"

    def move_down(self, delay):
        print("Schranke fährt runter.")
        GPIO.output(38, False)
        time.sleep(delay)
        print("Schranke ist unten.")
        GPIO.output(38, True)
        self.status = "down"

if __name__ == '__main__':
    bc = BarrierControl()
    GPIO.add_event_detect(36, GPIO.RISING, callback=bc.move_barrier, bouncetime=250)
    signal.pause()
 