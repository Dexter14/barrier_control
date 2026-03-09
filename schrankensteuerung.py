import time
import RPi.GPIO as GPIO
import signal
import sys
import yaml
from threading import Timer

def signal_handler(_sig, _frame):
    GPIO.cleanup()
    print('\nProgramm wird beendet.')    
    sys.exit(0)

# Signale registrieren (SIGINT = Ctrl+C, SIGTERM = Abbruchbefehl)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class BarrierControl:
    def __init__(self, config):
        print(str(config))
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(config['pin_down'], GPIO.OUT)
        GPIO.setup(config['pin_up'], GPIO.OUT)
        GPIO.setup(config['pin_button'], GPIO.IN)
        self.time_up = config['time_up']
        self.time_down = config['time_down']
        self.pin_up = config['pin_up']
        self.pin_down = config['pin_down']
        self.timer = None
        self._stop_moving("down")

    def move_barrier(self, _channel):
        if "down" == self.status:
            if self.timer != None:
                self.timer.cancel()
                self._stop_moving("up")
                return
            self.move_up(self.time_up)
        elif "up" == self.status:
            if self.timer != None:
                self.timer.cancel()
                self._stop_moving("down")
                return
            self.move_down(self.time_down)
        else:   
           raise ValueError

    def move_up(self, delay):
        self.timer = Timer(delay, self._stop_moving, args = ["up"])
        print("Schranke fährt hoch.")
        self._start_up()
        self.timer.start()
        

    def move_down(self, delay):
        self.timer =Timer(delay, self._stop_moving, args = ["down"])
        print("Schranke fährt runter.")
        self._start_down()
        self.timer.start()

    def _start_up(self):
        GPIO.output(self.pin_down, False)

    def _start_down(self):
        GPIO.output(self.pin_up, False)
  
    def _stop_moving(self, status):
        GPIO.output(self.pin_down, True)
        GPIO.output(self.pin_up, True)
        if "up" == status:
            print("Schranke ist oben.")
        elif "down" == status:
            print("Schranke ist unten.")
        self.status = status
        self.timer = None

if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    bc = BarrierControl(config)
    GPIO.add_event_detect(config['pin_button'], GPIO.RISING, callback=bc.move_barrier, bouncetime=250)
    signal.pause()
 