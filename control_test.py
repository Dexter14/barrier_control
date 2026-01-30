import time
import RPi.GPIO as GPIO
import signal
import sys
import config

def signal_handler(_sig, _frame):
    GPIO.cleanup()
    print('\nProgramm wird beendet.')    
    sys.exit(0)

# Signale registrieren (SIGINT = Ctrl+C, SIGTERM = Abbruchbefehl)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class BarrierControl():
    def __init__(self):
        print('Initialisierung')
        self.initial_delay = config.initial_delay
        self.delay = config.delay
        print(str(self.delay))
        self.pin_move_up = 37
        self.pin_move_down = 38
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_move_up, GPIO.OUT)
        GPIO.setup(self.pin_move_down, GPIO.OUT)
        GPIO.output(self.pin_move_up, True)
        GPIO.output(self.pin_move_down, True)
        self.move_down(self.initial_delay)

    def move_down(self, delay = self.delay):
        print("Schranke fährt runter.")
        GPIO.output(self.pin_move_down, False)
        time.sleep(delay)
        print("Schranke ist unten.")
        GPIO.output(self.pin_move_down, True)

    def move_up(self, delay = self.delay):
        print("Schranke fährt hoch.")
        GPIO.output(self.pin_move_up, False)
        time.sleep(1)
        print("Schranke ist oben.")
        GPIO.output(self.pin_move_up, True)

    def run(self):
        while True:
            input('.')
            self.move_up()
            input('.')
            self.move_down()


if __name__ == '__main__':
    b = BarrierControl()
    b.run()
        
