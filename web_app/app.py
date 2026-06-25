from flask import Flask, render_template, redirect, url_for
import os
import sys
import traceback

app = Flask(__name__)

# Make project root importable and initialize BarrierControl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from schrankensteuerung import create_barrier_control
    config_path = os.path.join(ROOT, 'config.yaml')
    try:
        bc = create_barrier_control(config_path)
    except Exception:
        print("Fehler beim Erstellen von BarrierControl:")
        traceback.print_exc()
        bc = None
except Exception:
    print("Fehler beim Importieren von schrankensteuerung:")
    traceback.print_exc()
    bc = None

@app.route("/klick_barrier", methods=["POST"])
def button_barrier():
    ergebnis_text = "Der Button Schranke wurde erfolgreich verarbeitet!"
    if bc:
        try:
            bc.move_barrier(None)
            ergebnis_text = "Schranke: Aktion ausgelöst."
        except Exception as e:
            ergebnis_text = f"Fehler beim Auslösen der Schranke: {e}"
    else:
        ergebnis_text = "BarrierControl nicht initialisiert."
    return render_template("index.html", nachricht=ergebnis_text)

@app.route("/klick_tor", methods=["POST"])
def button_tor():
    ergebnis_text = "Der Button Tor wurde erfolgreich verarbeitet!"
    if bc:
        try:
            bc.open_close_garage()
            ergebnis_text = "Garagentor: Aktion ausgelöst."
        except Exception as e:
            ergebnis_text = f"Fehler beim Garagentor: {e}"
    else:
        ergebnis_text = "BarrierControl nicht initialisiert."
    return render_template("index.html", nachricht=ergebnis_text)

def start():
    # Startet den Server im lokalen Netzwerk auf Port 5000
    app.run(host='192.168.178.43', port=5000, debug=True)

if __name__ == '__main__':
    start()