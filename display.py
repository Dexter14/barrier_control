import traceback
import sys
import time

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


def show_oled_message(message, duration_seconds=10):
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


def show_oled_scrolling_message(message, step_delay_seconds=0.02):
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


def show_oled_status_message(message):
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


def clear_oled_display():
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