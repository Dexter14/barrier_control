import time
import RPi.GPIO as GPIO
import signal
import sys
import yaml

def signal_handler(_sig, _frame):
    GPIO.cleanup()
    print('\nProgramm wird beendet.')    
    sys.exit(0)

# Signale registrieren (SIGINT = Ctrl+C, SIGTERM = Abbruchbefehl)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class BarrierControl():
    def __init__(self):
        with open("config.yaml", 'r') as file:
            self.config = yaml.safe_load(file)
        print('Initialisierung')
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.config['gpio_pin_up'], GPIO.OUT)
        GPIO.setup(self.config['gpio_pin_down'], GPIO.OUT)
        GPIO.setup(self.config['gpio_pin_button'], GPIO.IN)
        self.status = "down"

    def move_barrier(self, channel):
        if "down" == self.status:
            self.move_up(delay = self.config['delay'])
        elif "up" == self.status:
            self.move_down(delay = self.config['delay'])
        else:
            raise ValueError

    def move_down(self, *, delay):
        print("Schranke fährt runter.")
        self._close_relais_down()
        time.sleep(delay)
        print("Schranke ist unten.")
        self._open_relais_down()
        self.status = "down"

    def move_up(self, *, delay):
        print("Schranke fährt hoch.")
        self._close_relais_up()
        time.sleep(delay)
        print("Schranke ist oben.")
        self._open_relais_up()
        self.status = "up"

    def _close_relais_up(self):
        GPIO.output(self.config['gpio_pin_up'], False)

    def _open_relais_up(self):
        GPIO.output(self.config['gpio_pin_up'], True)
    
    def _close_relais_down(self):
        GPIO.output(self.config['gpio_pin_down'], False)
    
    def _open_relais_down(self):
        GPIO.output(self.config['gpio_pin_down'], True)

if __name__ == '__main__':
    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    b = BarrierControl()
    GPIO.add_event_detect(config['gpio_pin_button'], GPIO.RISING, callback=b.move_barrier, bouncetime=config['bouncetime'])
    signal.pause()

