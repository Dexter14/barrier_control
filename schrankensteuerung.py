import time
import RPi.GPIO as GPIO
import signal
import sys
from threading import Timer

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
        self._stop_moving("down")
        self.timer = None

    def move_barrier(self, _channel):
        if "down" == self.status:
            if self.timer != None:
                self.timer.cancel()
                self._stop_moving("up")
                return
            self.move_up(5)
        elif "up" == self.status:
            if self.timer != None:
                self.timer.cancel()
                self._stop_moving("down")
                return
            self.move_down(5)
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
        GPIO.output(37, False)

    def _start_down(self):
        GPIO.output(38, False)
  
    def _stop_moving(self, status):
        GPIO.output(37, True)
        GPIO.output(38, True)
        if "up" == status:
            print("Schranke ist oben.")
        elif "down" == status:
            print("Schranke ist unten.")
        self.status = status
        self.timer = None

if __name__ == '__main__':
    bc = BarrierControl()
    GPIO.add_event_detect(36, GPIO.RISING, callback=bc.move_barrier, bouncetime=250)
    signal.pause()
 