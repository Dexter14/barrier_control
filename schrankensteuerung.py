#! /usr/bin/python
import time
import RPi.GPIO as GPIO
import signal
import sys
import traceback
import yaml
from threading import Timer, Thread

OLED_PYTHON_DIR = '/home/laura/2.23inch-OLED-HAT-Code/Without scrolling/Raspberry Pi/python'
OLED_FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
]


def _sanitize_oled_text(text):
    """Keep text readable even if no unicode-capable TTF font is available."""
    replacements = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue',
        'ß': 'ss',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def _load_oled_font(preferred_size=12):
    """Load a TTF font with umlaut support; fallback to PIL default."""
    from PIL import ImageFont

    for font_path in OLED_FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, preferred_size), True
        except Exception:
            continue
    return ImageFont.load_default(), False


def _show_oled_message(message, duration_seconds=10):
    """Show a centered text message on the Waveshare OLED for a fixed duration."""
    try:
        if OLED_PYTHON_DIR not in sys.path:
            sys.path.append(OLED_PYTHON_DIR)

        from drive import SSD1305
        from PIL import Image, ImageDraw

        disp = SSD1305.SSD1305()
        disp.Init()

        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        font, unicode_font_ok = _load_oled_font(12)
        if not unicode_font_ok:
            message = _sanitize_oled_text(message)

        try:
            text_width, text_height = draw.textsize(message, font=font)
        except Exception:
            text_width, text_height = len(message) * 6, 8

        x = max(0, (width - text_width) // 2)
        y = max(0, (height - text_height) // 2)
        draw.text((x, y), message, font=font, fill=255)

        disp.getbuffer(image)
        disp.ShowImage()
        time.sleep(duration_seconds)

        # Blank the display again; keep interface open to avoid closed shared SPI handle.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        disp.getbuffer(image)
        disp.ShowImage()
    except Exception:
        print('OLED-Startup-Anzeige konnte nicht dargestellt werden:')
        traceback.print_exc()


def _show_oled_scrolling_message(message, step_delay_seconds=0.02):
    """Show a single-line marquee text from right to left once."""
    try:
        if OLED_PYTHON_DIR not in sys.path:
            sys.path.append(OLED_PYTHON_DIR)

        from drive import SSD1305
        from PIL import Image, ImageDraw

        disp = SSD1305.SSD1305()
        disp.Init()

        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        font, unicode_font_ok = _load_oled_font(12)
        if not unicode_font_ok:
            message = _sanitize_oled_text(message)

        try:
            text_width, text_height = draw.textsize(message, font=font)
        except Exception:
            text_width, text_height = len(message) * 6, 8

        y = max(0, (height - text_height) // 2)

        for x in range(width, -text_width - 1, -1):
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((x, y), message, font=font, fill=255)
            disp.getbuffer(image)
            disp.ShowImage()
            time.sleep(step_delay_seconds)

        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        disp.getbuffer(image)
        disp.ShowImage()
    except Exception:
        print('OLED-Lauftext konnte nicht dargestellt werden:')
        traceback.print_exc()


def _show_oled_status_message(message):
    """Show a centered status message on the Waveshare OLED (no timing, just display).
    Wraps text to multiple lines without breaking words.
    """
    try:
        if OLED_PYTHON_DIR not in sys.path:
            sys.path.append(OLED_PYTHON_DIR)

        from drive import SSD1305
        from PIL import Image, ImageDraw

        disp = SSD1305.SSD1305()
        disp.Init()

        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        font, unicode_font_ok = _load_oled_font(12)
        if not unicode_font_ok:
            message = _sanitize_oled_text(message)

        words = message.split()
        lines = []
        current_line = ""

        for word in words:
            try:
                test_line = current_line + (" " if current_line else "") + word
                text_width, _ = draw.textsize(test_line, font=font)
            except Exception:
                text_width = len(test_line) * 6

            if text_width <= width - 4:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        if len(lines) > 2:
            lines = lines[:2]

        try:
            _, text_height = draw.textsize("A", font=font)
        except Exception:
            text_height = 8

        total_height = len(lines) * text_height + (len(lines) - 1) * 2
        start_y = (height - total_height) // 2

        for idx, line in enumerate(lines):
            try:
                text_width, _ = draw.textsize(line, font=font)
            except Exception:
                text_width = len(line) * 6

            x = max(0, (width - text_width) // 2)
            y = start_y + idx * (text_height + 2)
            draw.text((x, y), line, font=font, fill=255)

        disp.getbuffer(image)
        disp.ShowImage()
    except Exception:
        print('OLED-Status-Anzeige konnte nicht dargestellt werden:')


def _clear_oled_display():
    """Clear the OLED display."""
    try:
        if OLED_PYTHON_DIR not in sys.path:
            sys.path.append(OLED_PYTHON_DIR)

        from drive import SSD1305
        from PIL import Image, ImageDraw

        disp = SSD1305.SSD1305()
        disp.Init()

        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        disp.getbuffer(image)
        disp.ShowImage()
    except Exception:
        pass

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
        oled_duration = config.get('oled_startup_duration', 10)
        try:
            oled_duration = float(oled_duration)
        except (TypeError, ValueError):
            oled_duration = 10

        oled_second_message = str(config.get('oled_second_message', '')).strip()
        oled_second_step_delay = config.get('oled_second_message_speed', 0.02)
        try:
            oled_second_step_delay = float(oled_second_step_delay)
        except (TypeError, ValueError):
            oled_second_step_delay = 0.02
        oled_second_step_delay = min(0.2, max(0.005, oled_second_step_delay))

        if oled_message and oled_duration > 0:
            _show_oled_message(oled_message, oled_duration)
        if oled_second_message:
            _show_oled_scrolling_message(oled_second_message, oled_second_step_delay)

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
                        _show_oled_status_message(text)
                        
                        display_clear_timer = Timer(timeout_duration, _clear_oled_display)
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
 