#! /usr/bin/python
import time
import RPi.GPIO as GPIO
import signal
import sys
import traceback
import yaml
import display
from threading import Timer, Thread




def signal_handler(_sig, _frame):
    global bc
    if bc and hasattr(bc, 'stop_monitor'):
        bc.stop_monitor()
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
        GPIO.setup(config['pin_garage'], GPIO.OUT)
        GPIO.setup(config['pin_button'], GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.time_up = config['time_up']
        self.time_down = config['time_down']
        self.pin_up = config['pin_up']
        self.pin_down = config['pin_down']
        self.pin_garage = config['pin_garage']
        self.timer = None
        self._oled_stop_event = False
        self._last_displayed_status = None
        self._display_timeout_thread = None

        oled_message = str(config.get('oled_startup_message', ''))
        oled_duration = float(config.get('oled_startup_duration', 1))
        display.show_oled_message(oled_message, oled_duration)
       
        oled_second_message = str(config.get('oled_second_message', ''))
        oled_second_step_delay = float(config.get('oled_second_message_speed', 0.02))
        display.show_oled_scrolling_message(oled_second_message, oled_second_step_delay)

        self.status = 'moving_down'
        
        self._monitor_thread = Thread(target=self._monitor_status_for_oled, daemon=True)
        self._monitor_thread.start()
        
        self.move_down(self.time_down)

    def _monitor_status_for_oled(self):
        """Background thread to monitor status changes and display on OLED."""
        status_text_map = {
            'up': 'Schranke ist oben',
            'down': 'Schranke ist unten',
            'moving_up': 'Schranke fährt hoch',
            'moving_down': 'Schranke fährt runter',
        }
        
        display_clear_timer = None
        timeout_duration = 30
        
        while not self._oled_stop_event:
            try:
                if self.status != self._last_displayed_status:
                    self._last_displayed_status = self.status
                    
                    if display_clear_timer is not None:
                        display_clear_timer.cancel()
                        display_clear_timer = None
                    
                    text = status_text_map.get(self.status, '')
                    if text:
                        display.show_oled_status_message(text)
                        
                        display_clear_timer = Timer(timeout_duration, display.clear_oled_display)
                        display_clear_timer.daemon = True
                        display_clear_timer.start()
                
                time.sleep(0.5)
            except Exception as e:
                print(f'OLED Monitor Fehler: {e}')
                traceback.print_exc()
                time.sleep(1)

    def open_close_garage(self):
        GPIO.output(self.pin_garage, False)
        time.sleep(1)
        GPIO.output(self.pin_garage, True)

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
            raise ValueError('Schrankenstatus nicht initialisiert.')

    def move_up(self, delay):
        self.status = "moving_up"
        self.timer = Timer(delay, self._stop_moving, args = ["up"])
        print("Schranke fährt hoch.")
        self._start_up()
        self.timer.start()

    def move_down(self, delay):
        self.status = "moving_down"
        self.timer =Timer(delay, self._stop_moving, args = ["down"])
        print("Schranke fährt runter.")
        self._start_down()
        self.timer.start()

    def _start_up(self):
        if self._stafty_check():
            GPIO.output(self.pin_down, False)

    def _start_down(self):
        if self._stafty_check():
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

    def _stafty_check(self):
        state_down = GPIO.input(self.pin_down)
        state_up = GPIO.input(self.pin_up)
        return state_down == state_up == 1

    def stop_monitor(self):
        """Stop the OLED monitor thread gracefully."""
        self._oled_stop_event = True
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2)


# Modulweite BarrierControl-Instanz (für Web-App-Zugriff)
bc = None


def create_barrier_control(config_path='config.yaml'):
    """Create and return a BarrierControl instance from a YAML config.

    This function also stores the instance in the module-level `bc` variable
    so other modules (z. B. die Web-App) darauf zugreifen können.
    """
    global bc
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    bc = BarrierControl(config)
    GPIO.add_event_detect(config['pin_button'], GPIO.FALLING, callback=bc.move_barrier, bouncetime=config.get('bouncetime', 200))
    return bc


if __name__ == '__main__':
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    bc = BarrierControl(config)
    GPIO.add_event_detect(config['pin_button'], GPIO.FALLING, callback=bc.move_barrier, bouncetime=config['bouncetime'])
    signal.pause()
 